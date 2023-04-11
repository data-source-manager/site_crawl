# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

import requests
from lxml import etree

from .base_parser import BaseParser


class BmvgParser(BaseParser):
    name = 'bmvg'
    
    # 站点id
    site_id = "0765887c-c000-4e86-b205-ab0e6fb32b74"
    # 站点名
    site_name = "德国防部网站"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "0765887c-c000-4e86-b205-ab0e6fb32b74", "source_name": "德国防部网站", "direction": "de", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91230d6c-2f72-11ed-a768-d4619d029786", "媒体库", "https://www.bmvg.de/service/queryListFilter/11056?&darkTheme=true&mediathek=true&requiresFallbackImage=true", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        items = response.json()
        for item in items['items']:
            item_url = item['linkHref']
            res = requests.get(item_url)
            new_url = etree.HTML(res.text).xpath('//section/div/div/a/@href')
            if new_url:
                yield new_url[0]

    def get_title(self, response) -> str:
        title = response.xpath('//title/text()').extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        author = response.xpath('//div[@class="c-contact--author-ref"]//dd//span/text()').extract()
        return author

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.xpath('//span/time/text()').extract_first() or ""
        if time_:
            return str(datetime.strptime(time_.strip(), "%d.%m.%Y"))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('//div[@class="c-rte--default"]//p|'
                                   '//div[@class="c-rte--default"]//strong|'
                                   '//div[@class="c-rte--default"]//strong/font|'
                                   '//section[3]//picture/img|'
                                   '//section[2]//picture/img')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", "li", "font"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
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
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": news_tag.attrib.get('title'),
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('alt'),
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
