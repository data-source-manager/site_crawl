# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

import langdetect

from .base_parser import BaseParser


class UsfjParser(BaseParser):
    name = 'usfj'
    
    # 站点id
    site_id = "f871f319-9cc4-477e-b4b8-413fb5ebaf98"
    # 站点名
    site_name = "驻日美军"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f871f319-9cc4-477e-b4b8-413fb5ebaf98", "source_name": "驻日美军", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("7bfbe881-7de7-3aa4-a4ca-57e1783a467d", "媒体", "", "政治"),
            ("912336a2-2f72-11ed-a768-d4619d029786", "媒体/新闻稿", "https://www.usfj.mil/Media/Press-Releases/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        urls = response.xpath('//a[@id="atitle"]/@href').extract()
        if urls:
            for url in urls:
                yield urljoin(response.url, url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@itemprop="headline"]/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        # 2022-01-21T03:21:00.2100000
        pub = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if pub:
            pub_time = str(datetime.strptime(pub.split(".")[0].replace("T", " "), "%Y-%m-%d %H:%M:%S"))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        img_list = response.xpath('//div[@class="image"]/img')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))

        news_tags = response.xpath('//div[@class="body"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "strong"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)

                if news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)
        return content

    def get_detected_lang(self, response) -> str:
        title = self.get_title(response)
        if title:
            return langdetect.detect(f"{title}")
        else:
            print('error, no title url:' + response.url)
            return ''

    def parse_text(self, news_tag):
        cons = news_tag.xpath('./text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    new_cons = ''.join([c for c in new_cons if c != ""])
                    if new_cons:
                        dic['data'] = x.strip()
                        dic['type'] = 'text'
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
