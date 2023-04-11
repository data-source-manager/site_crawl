# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import langdetect

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class VovvnParser(BaseParser):
    name = 'vovvn'
    
    # 站点id
    site_id = "c060a25b-5678-403b-a7b2-4032a7536d39"
    # 站点名
    site_name = "越南之声"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c060a25b-5678-403b-a7b2-4032a7536d39", "source_name": "越南之声", "direction": "vn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9123551a-2f72-11ed-a768-d4619d029786", "世界", "https://vov.vn/the-gioi", "政治"),
            ("9123554c-2f72-11ed-a768-d4619d029786", "军事和国防", "https://vov.vn/quan-su-quoc-phong", "军事"),
            ("912354f2-2f72-11ed-a768-d4619d029786", "政治", "https://vov.vn/chinh-tri", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//a[h5 or h3]/@href').extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        # 16.07.2022 – 23:42
        pub = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@class="text-long"]/p|//div[@class="content"]/*|//div[@class="content"]/figure/video|'
            '//div[@class="text-long"]/figure/div/article//img|'
            '//div[@class="video__summary"]|//div[@class="content"]/figure/img|'
            '//div[@class="row article-summary"]/div/h4/div|'
            '//div[@class="text-long"]//figcaption|//div[@class="text-long"]//img')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "div", "p", "figcaption", "em"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict.get("data"):
                        content.append(text_dict)
                if news_tag.root.tag == 'img':
                    img_dict = self.parse_img(response, news_tag)
                    if img_dict:
                        content.append(img_dict)
                if news_tag.root.tag == "video":
                    con_file = self.parse_media(response, news_tag)
                    if con_file:
                        content.append(con_file)
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
        video_src = urljoin(response.url, news_tag.xpath("./@src").extract_first())
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
