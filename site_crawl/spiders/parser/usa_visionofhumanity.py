# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class USA_visionofhumanityParser(BaseParser):
    name = 'usa_visionofhumanity'
    # 站点id
    site_id = "a8dcbf50-944d-4d8a-83f3-614339aae1d9"
    # 站点名
    site_name = "人类愿景"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "a8dcbf50-944d-4d8a-83f3-614339aae1d9", "source_name": "人类愿景", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91233d00-2f72-11ed-a768-d4619d029786", "报告和资源", "https://www.visionofhumanity.org/resources/?type=research", "政治"),
            ("91233cce-2f72-11ed-a768-d4619d029786", "最新文章", "https://www.visionofhumanity.org/news-articles/", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_node = response.xpath(
            "//div[@class='news-title']")
        if news_node:
            for node in news_node:
                news_url = node.xpath("./h3/a/@href").get()
                time = node.xpath("./h6/text()").get()
                title = node.xpath("./h3/a/text()").get()
                self.Dict[news_url] = {"dt": time, "title": title}
                yield news_url

    def get_title(self, response) -> str:
        title = self.Dict[response.url]['title']
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        if self.Dict[response.url]['dt']:
            pub = str(datetime_helper.fuzzy_parse_datetime(self.Dict[response.url]['dt']))
            return pub
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 提升作用域
        if ".pdf" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
            return content
        news_tags = response.xpath("//div[@class='block-paragraph-content']/*|//div[@class='block-image-content']/img")
        img_node = response.xpath("//meta[@property='og:image']/@content").get()
        if img_node:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_node) + '.jpg',
                   "description": None,
                   "src": img_node
                   }
            content.append(dic)
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", 'h5', "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
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
        img_url = urljoin(response.url, news_tag.attrib.get('data-src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
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
