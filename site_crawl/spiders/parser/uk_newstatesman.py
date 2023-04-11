# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import langdetect

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class NewstatesmanParser(BaseParser):
    name = 'newstatesman'
    
    # 站点id
    site_id = "34d0d275-287f-46bb-a84d-fd12807f276d"
    # 站点名
    site_name = "新政治家"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "34d0d275-287f-46bb-a84d-fd12807f276d", "source_name": "新政治家", "direction": "uk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("3808629f-eac3-3b8a-b5a9-f5fddf3c2336", "世界", "", "政治"),
            ("91234804-2f72-11ed-a768-d4619d029786", "世界/中国", "https://www.newstatesman.com/world/asia/china", "政治"),
            ("912346c4-2f72-11ed-a768-d4619d029786", "世界/亚洲", "https://www.newstatesman.com/world/asia", "政治"),
            ("9123489a-2f72-11ed-a768-d4619d029786", "世界/印度", "https://www.newstatesman.com/world/asia/india", "政治"),
            ("91234638-2f72-11ed-a768-d4619d029786", "世界/欧洲", "https://www.newstatesman.com/world/europe", "政治"),
            ("91234746-2f72-11ed-a768-d4619d029786", "世界/美洲", "https://www.newstatesman.com/world/americas", "政治"),
            ("2714134b-2c2e-37c6-8bf0-8c4cdcae1503", "国际政治", "", "政治"),
            ("912345a2-2f72-11ed-a768-d4619d029786", "国际政治/地缘政治", "https://www.newstatesman.com/international-politics/geopolitics", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//h3/a/@href').extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = response.xpath('//p[@class="c-article-header__author"]/a/text()').extract()
        if authors:
            return [x.strip() for x in authors]
        return []

    def get_pub_time(self, response) -> str:
        pub = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        tags = response.xpath('//div[@class="c-tags"]/a/text()').extract()
        if tags:
            return [x.strip() for x in tags]
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@class="c-article-content__container"]/p|'
            '//div[@class="c-article-content__container"]/div[@class="c-featured-image"]//img')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p"]:
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
