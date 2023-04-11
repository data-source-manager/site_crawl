# -*- coding: utf-8 -*-
import datetime
from urllib.parse import urljoin

import requests
from scrapy import Selector

from .base_parser import BaseParser


class CgsrParser(BaseParser):
    name = 'cgsr'
    
    # 站点id
    site_id = "3be910a3-1930-4c6e-a376-7386acdf0abb"
    # 站点名
    site_name = "美国利弗莫尔国家实验室全球安全研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "3be910a3-1930-4c6e-a376-7386acdf0abb", "source_name": "美国利弗莫尔国家实验室全球安全研究中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91230060-2f72-11ed-a768-d4619d029786", "出版物", "https://cgsr.llnl.gov/research", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.pdfDict = {}

    def parse_list(self, response) -> list:
        news_urls = [urljoin(response.url, x) for x in response.xpath('//div[@class="span3"]/a/@href').extract()][
                    0:2] or []
        for x in news_urls:
            if "livermore-papers" in x or "occasional-papers" in x:
                all_urls = Selector(text=requests.get(x).text).xpath('//div[@class="span5"]|//div[@class="span6"]')
                for x in all_urls:
                    href = urljoin(response.url, x.xpath(".//a/@href").extract_first())
                    title = x.xpath(".//a/text()").extract_first()
                    author = x.xpath(".//h4/text()").extract_first()
                    publish = x.xpath(".//p/text()").extract_first()
                    if "pdf" in href:
                        self.pdfDict[href] = {
                            "title": title.strip(),
                            "author": author.strip(),
                            "publish": publish.strip()
                        }
                    yield href

    def get_title(self, response) -> str:
        if "pdf" in response.url:
            return self.pdfDict[response.url]["title"]
        return ""

    def get_author(self, response) -> list:
        if "pdf" in response.url:
            return [self.pdfDict[response.url]["author"]]
        return []

    def get_pub_time(self, response) -> str:
        if "pdf" in response.url:
            publish = self.pdfDict[response.url]["publish"]
            return str(datetime.datetime.strptime(publish, "%B %Y"))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        return [{
            "type": "file",
            "src": response.url,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(response.url) + ".pdf"
        }]

    def get_detected_lang(self, response) -> str:
        return "en"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url, news_tag.xpath("").extract_first())
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
