# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class UsanavalsafetycenterParser(BaseParser):
    name = 'Usanavalsafetycenter'
    
    # 站点id
    site_id = "8820dc4c-f9d6-475f-a056-ec22e23644a8"
    # 站点名
    site_name = "美国海军安全中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "8820dc4c-f9d6-475f-a056-ec22e23644a8", "source_name": "美国海军安全中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91231d98-2f72-11ed-a768-d4619d029786", "消息", "https://navalsafetycommand.navy.mil/Media/News/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.urltimedict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//span[@class="title"]/a/@href').extract()
        for news in news_urls:
            yield news

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="twitter:title"]/@content').extract_first(default="") or ""
        title = title.strip() or ""
        return title

    def get_author(self, response) -> list:
        author = response.xpath('//p/span/text()').extract_first()
        if author.startswith('By '):
            author = author[3:]
        return [author]

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first(default="")
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
            return str(pub_time)
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('//div[@class="image"]/img|'
                                   '//div[@class="body"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                if news_tag.root.tag == 'div':
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "en"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append({'data': x.strip(), 'type': 'text'})
        return new_cons

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": news_tag.attrib.get('alt'),
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
