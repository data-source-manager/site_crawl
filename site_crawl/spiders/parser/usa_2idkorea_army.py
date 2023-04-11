# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from .base_parser import BaseParser


class Usa_2idkorea_armyParser(BaseParser):
    name = 'usa_2idkorea_army'
    # 站点id
    site_id = "cf0afce1-fabc-462c-b3fe-4821789ee6ad"
    # 站点名
    site_name = "美国陆军第2步兵师"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "cf0afce1-fabc-462c-b3fe-4821789ee6ad", "source_name": "美国陆军第2步兵师", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91231eba-2f72-11ed-a768-d4619d029786", "报告", "https://www.2id.korea.army.mil/Media-Hub/The-Indianhead/", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//div[contains(@id,'HtmlModule_lblContent')]/div/a[position()<21]/@href").extract() or ""
        if news_urls:
            for news_url in (news_urls):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//title/text()").extract_first() or ""
        return title

    def get_author(self, response) -> list:
        pass

    def get_pub_time(self, response) -> str:
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        pass

    def get_content_media(self, response) -> list:
        content = []
        file_dict = self.parse_file(response)
        if file_dict:
            content.append(file_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, response, news_tag):
        return []

    def parse_img(self, response, news_tag, xpath_src='', xpath_des=''):
        pass

    def parse_file(self, response):
        file_src = response.url
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag, xpath_src='', xpath_des=''):
        video_src = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": news_tag.xpath(xpath_des).extract_first(),
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
