# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from .base_parser import BaseParser


class UsawcParser(BaseParser):
    name = 'usawc'
    
    # 站点id
    site_id = "2fdb80c8-47fe-aa57-2568-1a28eb7b6742"
    # 站点名
    site_name = "海军军事学院海战研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "2fdb80c8-47fe-aa57-2568-1a28eb7b6742", "source_name": "海军军事学院海战研究中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块主题)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f12001a5-39ef-3397-97b6-4d4999027c02", "研究中心", "", "政治"),
            ("9122ff02-2f72-11ed-a768-d4619d029786", "研究中心/俄罗斯海事", "https://usnwc.edu/Research-and-Wargaming/Research-Centers/Russia-Maritime-Studies-Institute", "政治"),
        ]
    ]


    def __init__(self):
        BaseParser.__init__(self)
        self.urltimedict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[contains(@class,"eg-program-slider")]/@href').extract() or []
        if news_urls:
            for news in list(set(news_urls)):
                url = urljoin(response.url, news)
                yield url

    def get_title(self, response) -> str:
        title = response.xpath('//h2[@class="subTitle"]/text()').extract_first(default="") or response.xpath(
            '//h2/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('//div[@class="entry-content"]/p|'
                                   '//div[@class="entry-content"]/p/img|'
                                   '//div[contains(@class,"genProgDetai")]/div//p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
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
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
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
