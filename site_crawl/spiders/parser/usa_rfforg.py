# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

import langdetect

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class RfforgParser(BaseParser):
    name = 'rfforg'
    
    # 站点id
    site_id = "dbbc2978-b0df-414d-8275-fc241daeec83"
    # 站点名
    site_name = "未来资源研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "dbbc2978-b0df-414d-8275-fc241daeec83", "source_name": "未来资源研究所", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("2334e541-9703-3c7b-b742-f3f3d0856829", "出版物", "", "政治"),
            ("91232e50-2f72-11ed-a768-d4619d029786", "出版物/报告", "https://www.rff.org/api/v2/pages/?base_type=core.BasePage&fields=introduction%2Cpublication_type%28title%29%2Cpublication_cover_fill_197x254&limit=12&order=-first_published_at&publication_type=14&type=publications.PublicationPage", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        json_data = re.findall('<a href="(https://www.rff.org/publications.*?)" rel="nofollow">', response.text)
        for item in json_data:
            yield item

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="hero__title"]/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        author_list = []

        authors = "".join(response.xpath('//p[@class="hero-meta__column-content"]//text()').extract())
        if "and" in authors:
            authors = authors.replace("and", ",")
        if "," in authors:
            authors = authors.split(",")
        for au in authors:
            if au.strip():
                author_list.append(au.strip())
        return author_list

    def get_pub_time(self, response) -> str:
        # 16.07.2022 – 23:42
        pub = response.xpath('//p[@class="hero-meta__column-date"]/text()').extract_first()
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub.strip())
            pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        tags = response.xpath('//li[@class="tags-list__tag"]/a/text()').extract()
        if tags:
            return [x.strip() for x in tags]
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@class="rich-text"]/p|'
            '//div[@class="rich-text"]/ul/li|'
            '//figure[@class="sf-image__figure"]/img|'
            '//div[@class="hero__content"]//a[contains(text(), "Download")]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "li", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict.get("data"):
                        content.append(text_dict)
                if news_tag.root.tag == 'a':
                    file_dict = self.parse_file(response, news_tag)
                    if file_dict:
                        content.append(file_dict)
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
        img_url = news_tag.attrib.get('srcset').split(',')[0].split(' ')[0]
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('alt'),
               "src": img_url
               }
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("./@href").extract_first())
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
