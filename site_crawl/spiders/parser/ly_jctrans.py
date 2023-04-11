# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class LY_jctransParser(BaseParser):
    name = 'ly_jctrans'
    
    # 站点id
    site_id = "507842d1-d58f-45c5-a444-5dc8e9fbc37f"
    # 站点名
    site_name = "自由和发展研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "507842d1-d58f-45c5-a444-5dc8e9fbc37f", "source_name": "自由和发展研究中心", "direction": "ly", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8ce596-fe6f-11ec-a30b-d4619d029786", "消息", "https://lyd.org/noticias/page/1/", "政治"),
            ("4a8ce60e-fe6f-11ec-a30b-d4619d029786", "消息/观点", "https://lyd.org/category/opinion/", "政治"),
            ("4a8ce88e-fe6f-11ec-a30b-d4619d029786", "消息/调查", "https://lyd.org/category/encuestas/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.dict = {}

    def parse_list(self, response) -> list:
        if "encuestas" in response.url:
            news_node = response.xpath('//section[@class="news"]//div[contains(@class,"studio-lista")]')
            if news_node:
                for new_node in news_node:
                    title = new_node.xpath(".//h3/text()").get()
                    rsp_url = new_node.xpath(".//a/@href").get()
                    year, mt = re.findall('/(\d{4})/(\d{1,2})/', rsp_url)[0]
                    self.dict[rsp_url] = {"time": year + "-" + mt + "-" + "01", "title": title}
                    yield urljoin(response.url, rsp_url)
        else:
            news_urls = response.xpath(
                '//section[@class="news"]//div[contains(@class,"img-wrapper-zoom")]/a/@href').extract() or ""
            if news_urls:
                for news_url in news_urls:
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if ".pdf" in response.url:
            title = self.dict[response.url]['title']
            return title
        else:
            title = response.xpath('//header[@class="entry-header text-center"]/h1/text()').extract_first(default="")

        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if ".pdf" in response.url:
            time_ = self.dict[response.url]['time']
        else:
            time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        if ".pdf" in response.url:
            return tags_list
        else:
            tags = response.xpath('//footer[@class="entry-footer"]/div[@class="tags"]/a/text()').getall()
            if tags:
                for tag in tags:
                    if tag.strip():
                        tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []
        if ".pdf" in response.url:
            return content
        else:
            news_tags = response.xpath('//div[@class="entry-content"]/*')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                        if news_tag.xpath(".//img"):
                            con_img = self.parse_img(response, news_tag)
                            if con_img:
                                content.append(con_img)
                        text_dict = self.parse_text(news_tag)
                        if text_dict:
                            content.append(text_dict)
                    if news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            con_text = self.parse_text(con)
                            if con_text:
                                content.append(con_text)
                    if news_tag.root.tag == "img":
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip()
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@data-lazy-src').extract_first()

        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": None,
                   "src": img_url
                   }
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath(".//@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.attrib.get('title'),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag, media_type):
        videoUrl = news_tag.xpath("").extract_first()
        if media_type == "video":
            suffix = ".mp4"
        else:
            suffix = ".mp3"
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }
            return video_dic

    def get_like_count(self, response) -> int:
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
