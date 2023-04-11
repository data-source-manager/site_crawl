# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from .base_parser import BaseParser


class UsaceParser(BaseParser):
    name = 'usace'
    
    # 站点id
    site_id = "2403c86d-4a7a-4d5b-87e6-ea0270ed9aae"
    # 站点名
    site_name = "美国陆军工程与支援中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "2403c86d-4a7a-4d5b-87e6-ea0270ed9aae", "source_name": "美国陆军工程与支援中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("08a16000-c2e7-3e77-98e0-c59cf3e8a8de", "媒体", "", "政治"),
            ("9123284c-2f72-11ed-a768-d4619d029786", "媒体/新闻发布", "https://www.hnc.usace.army.mil/Media/News-Releases/", "政治"),
            ("91232748-2f72-11ed-a768-d4619d029786", "媒体/新闻故事", "https://www.hnc.usace.army.mil/Media/News-Stories/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.urltimedict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h3/a/@href').extract() or []
        if news_urls:
            for news in news_urls:
                yield urljoin(response.url, news)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="title"]/text()').extract_first(default="") or ""

        return title.strip() or ""

    def get_author(self, response) -> list:
        author = response.xpath('//div[@class="info"]/div/a/text()').extract_first()
        if author:
            author = author.replace("By", "")
            if "," in author:
                author = author.split(",")[0].strip()
            return author.strip()

    def get_pub_time(self, response) -> str:
        new_time = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if new_time:
            new_time = new_time.replace("T", " ").split(".")[0]
            return new_time.strip()
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return response.xpath('//div[@class="tags"]/div/a/text()').extract()

    def get_content_media(self, response) -> list:
        content = []
        images = response.xpath('//div[contains(@class,"item")]')
        for img in images:
            img_url = urljoin(response.url, img.xpath('.//div[@class="slide"]/img/@href').extract_first())
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": response.xpath('.//div[@class="media-caption subtle"]/p/text()').extract_first(),
                   "src": img_url}
            content.append(dic)
        news_tags = response.xpath('//div[@itemprop="articleBody"]/p')
        if news_tags:
            for news_tag in news_tags:
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
                if "_____" in x:
                    continue
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
