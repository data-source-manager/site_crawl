# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from util.time_deal.translatetTime import ruDict
from .base_parser import BaseParser


class WciomParser(BaseParser):
    name = 'wciom'
    
    # 站点id
    site_id = "55f31e98-a7ce-486c-bbb8-f2e80cc22263"
    # 站点名
    site_name = "全俄社会舆论调查中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "55f31e98-a7ce-486c-bbb8-f2e80cc22263", "source_name": "全俄社会舆论调查中心", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("d7688fdc-12f9-4886-bf12-d6ea066171a9", "全俄社会舆论调查中心", "https://www.wciom.ru/tematicheskii-katalog/politics", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.urltimedict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@class="news-list"]/@href').extract() or []
        if news_urls:
            for news in news_urls:
                yield urljoin(response.url, news)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="post-hdr"]/text()').extract_first(default="") or ""

        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        new_time = response.xpath('//div[@class="post-date mob-d-none"]/text()').extract_first()
        if new_time:
            new_time = new_time.split(" ")
            new_time[1] = ruDict[new_time[1]]
            new_time = " ".join(new_time)
        return str(datetime.strptime(new_time, "%d %m %Y"))

    def get_tags(self, response) -> list:
        return response.xpath('//div[@class="tags"]/a/span/text()').extract()

    def get_content_media(self, response) -> list:
        content = []

        img_url = urljoin(response.url, response.xpath('//figure[@class="post-img"]/img/@href').extract_first())
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": img_url
               }
        content.append(dic)
        news_tags = response.xpath('//main/div[contains(@id,"c17")][1]/*|//main/div[@class="post-short mob-display"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p", "li"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
        file_src = response.xpath('//div[@class="downloads"]/ul/li/a/@href').extract_first()
        if file_src:
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            content.append(file_dic)
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
            if new_cons:
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
