# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class RU_carnegieParser(BaseParser):
    name = 'ru_carnegie'
    
    # 站点id
    site_id = "f5c1a410-84cf-40d7-83bb-19231d3eed80"
    # 站点名
    site_name = "卡内基莫斯科中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f5c1a410-84cf-40d7-83bb-19231d3eed80", "source_name": "卡内基莫斯科中心", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91233670-2f72-11ed-a768-d4619d029786", "出版物", "https://carnegie.ru/publications/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//h4/a/@href').extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                if "http" not in response.url:
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath(
            "//h1[@class='white-text narrow-line-height']/text()|//h1[@class='headline']/text()").extract_first(
            default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        author = response.xpath("//meta[@name='author']/@content").extract_first()
        if author:
            authors.append(author)
        return authors

    def get_pub_time(self, response) -> str:
        pub = response.xpath(
            "//div[@class='smaller-text gutter-half-bottom cyrillic-normal-book']/text()").extract_first()
        if pub:
            day, mt, year = pub.split(".")
            dt = year + "-" + mt + "-" + day
            return str(datetime_helper.fuzzy_parse_datetime(dt))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        if "policies" in response.url:
            tags = response.xpath('//meta[@name="keywords"]/@content').extract_first().split(",")
            if tags:
                return tags
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 提升作用域
        header_img = response.xpath("//meta[@name='twitter:image']/@content").extract_first()
        if header_img:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(header_img) + '.jpg',
                   "description": None,
                   "src": header_img
                   }
            content.append(dic)

        news_tags = response.xpath(
            '//div[@class="article-body"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p"]:
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
