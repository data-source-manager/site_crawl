# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import langdetect

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class GmfusParser(BaseParser):
    name = 'gmfus'
    
    # 站点id
    site_id = "271e59f9-6d18-4798-845a-b3f709e61046"
    # 站点名
    site_name = "德国马歇尔基金会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "271e59f9-6d18-4798-845a-b3f709e61046", "source_name": "德国马歇尔基金会", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91232ee6-2f72-11ed-a768-d4619d029786", "政策见解", "https://www.gmfus.org/policy-insights", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        items = response.xpath('//div[@class="card--text"]')
        if items:
            for item in items:
                news_url = item.xpath('./div[@class="card--title"]/h3/a/@href').extract_first(default="")
                self.tags = item.xpath('.//div[@class="article-header--tag"]/a/text()').extract()
                news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="pageheader__title"]/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = response.xpath(
            '//div[@class="headband__author-names--inner"]//a/text() | //div[@class="headband__author-names--inner"]/div/text()').extract()
        if authors:
            return [x.strip() for x in authors]
        return []

    def get_pub_time(self, response) -> str:
        # 16.07.2022 – 23:42
        pub = response.xpath('//div[@class="pageheader__date"]/text()').extract_first()
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
            pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        tags = self.tags
        if tags:
            return [x.strip() for x in tags]
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@class="p-container--small"]/div[@class="p__inner"]//span|'
            '//div[@class="p-container"]/div[@class="p__inner"]//img')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict.get("data"):
                        content.append(text_dict)
                if news_tag.root.tag == 'img':
                    img_dict = self.parse_img(response, news_tag)
                    if img_dict:
                        content.append(img_dict)
        return content

    def get_detected_lang(self, response) -> str:
        title = self.get_title(response)
        if title:
            return langdetect.detect(f"{title}")
        else:
            print('error, no title url:' + response.url)
            return ''

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('./text()').extract() or ""
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

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('alt'),
               "src": img_url
               }
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath(".//a/text()").extract_first(),
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
