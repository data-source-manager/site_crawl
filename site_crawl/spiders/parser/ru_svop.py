# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class SvopParser(BaseParser):
    name = 'svop'
    # 站点id
    site_id = "476f0668-22e5-46e3-b423-a81c2c3da61a"
    # 站点名
    site_name = "俄罗斯外交与国防政策委员会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "476f0668-22e5-46e3-b423-a81c2c3da61a", "source_name": "俄罗斯外交与国防政策委员会", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("912311b8-2f72-11ed-a768-d4619d029786", "消息", "http://svop.ru/category/news/", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@id="content"]/div[@class="clearfloat"]/div/a[@class="thumb left"]/@href').extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//h2[@class="title"]/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        # 16.07.2022 – 23:42
        pub = response.xpath('//div[@id="stats"]/span[@class="left"]/text()').extract_first()
        if pub:
            pub_time = str(datetime.strptime(pub, "%d.%m.%Y – %H:%M"))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        if "policies" in response.url:
            tags = response.xpath('//meta[@name="keywords"]/@content').extract_first().split(",")
            if tags:
                return tags
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@class="entry clearfloat"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict.get("data"):
                        content.append(text_dict)
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

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": response.xpath(".//p/text()").extract_first(),
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
