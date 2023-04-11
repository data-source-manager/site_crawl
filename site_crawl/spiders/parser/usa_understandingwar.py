# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class UnderstandingwarParser(BaseParser):
    name = 'understandingwar'
    
    # 站点id
    site_id = "c1c4a3a9-4a53-4041-a8a9-6d167d66ed2a"
    # 站点名
    site_name = "战争研究学院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c1c4a3a9-4a53-4041-a8a9-6d167d66ed2a", "source_name": "战争研究学院", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8bd2be-fe6f-11ec-a30b-d4619d029786", "出版物", "https://www.understandingwar.org/publications", "政治"),
            ("e595b024-461c-d5c5-ae62-c70e7afa36da", "研究", "", "政治"),
            ("3aaa27e3-432a-49d1-ba29-72fe2714f1f4", "研究/军事学习与战争的未来", "https://www.understandingwar.org/military-learning-and-future-war-project", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "c1c4a3a9-4a53-4041-a8a9-6d167d66ed2a"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h2/a/@href|//p[contains(@style,"font-size")]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@id="page-title"]/text()|//h1[@class="title"]/font/font/text()').extract_first(
            default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath(
            '//div[contains(@class,"author")]//div[@class="field-items"]//font/font/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[@property="dc:date dc:created"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        file = response.xpath('//div[contains(@class,"field-name-field-pdf")]//a/@href').extract_first()
        if file:
            file_dic = {
                "type": "file",
                "src": file,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(file) + ".pdf"
            }
            content.append(file_dic)
        news_tags = response.xpath('//div[@class="field-items"]/div[@property="content:encoded"]/*|'
                                   '//div[@class="field-items"]/div/div/*|'
                                   '//div[@class="field-items"]/div/div//p/a')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "ul"]:
                    if news_tag.xpath(".//img").extract():
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)
                    elif news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            news_tag = con
                            text_dict = self.parseOnetext(news_tag)
                            if text_dict:
                                content.extend(text_dict)
                    elif news_tag.root.tag == "a":
                        con_file = self.parse_file(response, news_tag)
                        if con_file:
                            content.append(con_file)
                    else:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            content.extend(text_dict)

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
                   "description": "".join(news_tag.xpath('.//img/@alt').extract()).strip(),
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

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("").extract_first()
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + ".mp4"
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
