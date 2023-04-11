# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class IN_capsindiaParser(BaseParser):
    name = 'in_capsindia'
    
    # 站点id
    site_id = "be996d21-acb6-4807-818e-4a960273e8b3"
    # 站点名
    site_name = "印度空中力量研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "be996d21-acb6-4807-818e-4a960273e8b3", "source_name": "印度空中力量研究中心", "direction": "in", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8dc042-fe6f-11ec-a30b-d4619d029786", "核安全", "https://capsindia.org/nuclear-security/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "nuclear-security" in response.url:
            news_items = response.xpath('//h3[contains(@class,"entry-title")]')
            for item in news_items:
                url = item.xpath("./a/@href").get()
                title = item.xpath("./a//text()").get()
                if url:
                    self.Dict[url] = {"title": title}
                    yield url
        else:
            news_items = response.xpath('//div[@class="tdc-content-wrap"]//div[@class="tdc-row"]/p')
            for item in news_items:
                url = item.xpath(".//a/@href").get()
                title = item.xpath(".//a/text()").get()
                date_str = item.xpath("./text()").get()
                if "|" in date_str:
                    date_str = date_str.split("|")[1]
                if url:
                    self.Dict[url] = {"title": title, "dt": date_str}
                    yield url

    def get_title(self, response) -> str:
        title = self.Dict[response.url].get('title')
        if not title:
            title = response.xpath('//h1[@class="tdb-title-text"]/text()').extract_first()
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []

        return authors

    def get_pub_time(self, response) -> str:
        data_str = self.Dict[response.url].get('dt')
        if not data_str:
            data_str = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if data_str:
            dt = datetime_helper.fuzzy_parse_timestamp(data_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        if response.url.endswith(".pdf"):
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
            return content

        news_tags = response.xpath("//iframe[@class='gde-frame']/@src")
        if news_tags:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
        else:
            img = response.xpath('//meta[@property="og:image"]/@content').extract_first()
            if img:
                dic = {"type": "image",
                       "name": None,
                       "md5src": self.get_md5_value(img) + '.jpg',
                       "description": "",
                       "src": img}
                content.append(dic)
            news_tags = response.xpath('//div[contains(@class,"td-post-content")]/div/*')
            if news_tags:
                for tag in news_tags:
                    if tag in ["h3", "h4", "p"]:
                        con = self.parse_text(tag)
                        if con.get("data"):
                            content.append(con)
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
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
                   "src": img_url}
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
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
