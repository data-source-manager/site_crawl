# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class CnCcgParser(BaseParser):
    name = 'ccg'
    
    # 站点id
    site_id = "54d2aebd-5156-40d6-98fc-7cfb7e507777"
    # 站点名
    site_name = "全球化智库"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "54d2aebd-5156-40d6-98fc-7cfb7e507777", "source_name": "全球化智库", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8c5ad6-fe6f-11ec-a30b-d4619d029786", "新闻", "http://en.ccg.org.cn/News", "政治"),
            ("7cc4570a-a681-44c7-8f34-d2d053bd3ebb", "研究报告", "http://en.ccg.org.cn/report", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.title = {}

    def parse_list(self, response) -> list:
        if "report" in response.url:
            news_urls = response.xpath('//div[@class="book-box"]/a')
            if news_urls:
                for news_url in list(set(news_urls)):
                    url = urljoin(response.url, news_url.xpath('./@href').extract_first())
                    if "pdf" in url:
                        title = news_url.xpath('./text()').extract_first()
                        self.title[url] = title
                    if "http://en.ccg.org.cn/report" == url:
                        continue
                    yield url
        else:
            news_urls = response.xpath('//ul[@class="huodong-list"]/li/a/@href|'
                                       '//div[@class="book-box"]/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    url = urljoin(response.url, news_url)
                    if "http://en.ccg.org.cn/report" == url:
                        continue
                    yield url

    def get_title(self, response) -> str:
        if "pdf" in response.url:
            return self.title[response.url]
        title = response.xpath('//title/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "pdf" in response.url:
            return "9999-01-01 00:00:00"
        time_ = response.xpath('//span[@class="time"]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        if "pdf" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
        else:
            img_set = set()
            img_list = response.xpath('//div[@class="row baogao-content"]/div[@class="col-sm-3 col-xs-12"]')
            if img_list:
                for img in img_list:
                    con_img = self.parse_img(response, img)
                    if con_img:
                        if not con_img["src"] in img_set:
                            content.append(con_img)
                            img_set.add(con_img["src"])

            news_tags = response.xpath('//div[@class="pinpai-page meiti-page"]//p|'
                                       '//div[@class="baogao-page"]/p|'
                                       '//div[@class="baogao-page"]/div/div')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                    if news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            con_text = self.parseOnetext(con)
                            if con_text:
                                content.extend(con_text)
                    if news_tag.root.tag == "div":
                        if news_tag.xpath('.//img').extract():
                            con_img = self.parse_img(response, news_tag)
                            if con_img:
                                if not con_img["src"] in img_set:
                                    content.append(con_img)
                                    img_set.add(con_img["src"])
                        file = news_tag.xpath('./a/@href').extract_first()
                        if file:
                            if "pdf" in file:
                                con_file = self.parse_file(response, news_tag)
                                if con_file:
                                    if not con_file["src"] in img_set:
                                        content.append(con_file)
                                        img_set.add(con_file["src"])

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

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
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//figcaption//text()').extract()).strip(),
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
