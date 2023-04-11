# -*- coding: utf-8 -*-
import json
from datetime import datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class HistoryParser(BaseParser):
    name = 'history'
    # 站点id
    site_id = "af993bd1-86b5-4716-be94-824724803cae"
    # 站点名
    site_name = "美国海军历史与遗产司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "af993bd1-86b5-4716-be94-824724803cae", "source_name": "美国海军历史与遗产司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91232716-2f72-11ed-a768-d4619d029786", "2022新闻", "https://www.history.navy.mil/news-and-events/news/2022/jcr:content.newsRollup.json", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.urltimedict = {}

    def parse_list(self, response) -> list:
        josnData = json.loads(response.text)["pages"]
        for x in josnData:
            yield urljoin(response.url, x["url"])

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="articleTitle partWidth"]/text()').extract_first(default="") or ""
        if title:
            return title.strip()
        return ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        # July 12, 2022
        new_time = response.xpath('//div[@class="date"]/div/text()').extract_first()
        if new_time:
            return str(datetime.strptime(new_time.strip(), "%B %d, %Y"))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return response.xpath('//div[@class="tags"]/div/a/text()').extract()

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            '//div[@class="articleParbody parsys"]/div/p|//div[@class="articleParbody parsys"]/div/div/div[@class="mediaAsset"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "div":
                    content.append(self.parse_img(response, news_tag))
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p", "li"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "en"

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
        img_url = urljoin(response.url, news_tag.xpath(".//img/@src").extract_first())
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": "".join(news_tag.xpath('.//div[@class="altCap"]/p//text()').extract()),
               "src": img_url
               }
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
