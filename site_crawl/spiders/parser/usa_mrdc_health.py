# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

import langdetect

from .base_parser import BaseParser


class MrdcParser(BaseParser):
    name = 'mrdc'
    
    # 站点id
    site_id = "9716f736-9c81-9d87-f75f-2f7a1c264f72"
    # 站点名
    site_name = "美国军队医学研究发展司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "9716f736-9c81-9d87-f75f-2f7a1c264f72", "source_name": "美国军队医学研究发展司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块主题)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91233af8-2f72-11ed-a768-d4619d029786", "文章", "https://mrdc.health.mil/index.cfm/media/articles", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.DICT1 = {}

    def parse_list(self, response) -> list:
        urls = response.xpath('//div[@id="this-accordion"]/div[1]//ul/li/a/@href').extract()
        if urls:
            for url in urls:
                yield urljoin(response.url, url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        author = response.xpath('//meta[@name="author"]/@content').extract_first()
        if author:
            return [author]
        return []

    def get_pub_time(self, response) -> str:
        # 2022-01-21T03:21:00.2100000
        pub = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if pub:
            pub_time = str(datetime.strptime(pub, "%B %d, %Y"))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        tag_list = []
        tags = response.xpath('//div[@class="tags"]//a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tag_list.append(tag.strip())
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="photo-box-wrap"]')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))

        news_tags = response.xpath(
            '//div[@id="news-content"]/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parse_text(news_tag)
                    content.extend(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        title = self.get_title(response)
        if title:
            return langdetect.detect(f"{title}")
        else:
            print('error, no title url:' + response.url)
            return ''

    def parse_text(self, news_tag):
        first_con = news_tag.xpath("./span/text()").extract_first().strip()
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)
        new_cons[0]["data"] = first_con + new_cons[0]["data"]
        return new_cons

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.xpath(".//img/@href"))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.xpath('//div[@class="photo-box-text"]/text()').extract_first().strip(),
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
