# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Usa_navsea_navymilParser(BaseParser):
    name = 'usa_navsea_navymil'
    
    # 站点id
    site_id = "371c7625-40e1-4ff9-956d-31124d6ea06c"
    # 站点名
    site_name = "美国海军海洋体系司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "371c7625-40e1-4ff9-956d-31124d6ea06c", "source_name": "美国海军海洋体系司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("5ff53611-e953-3e2b-94b8-0c1553f7ea73", "媒体", "", "政治"),
            ("91232b8a-2f72-11ed-a768-d4619d029786", "媒体/消息", "https://www.navsea.navy.mil/Media/News/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.pdfUrl = ""

    def parse_list(self, response) -> list:
        url_list = response.xpath("//span[@id='linkTitle']/a[contains(@id,'atitle')]/@href").extract()
        if url_list:
            for x in url_list:
                yield x

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='header']/h1[@class='title']/text()").extract_first(default="") or ""
        if title:
            return title.strip()
        return ""

    def get_author(self, response) -> list:
        author = response.xpath('//h2[@class="author"]/text()').extract_first()
        if author:
            return [author.replace("From", "").strip()]
        return []

    def get_pub_time(self, response) -> str:
        new_time = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if new_time:
            pub_time = datetime_helper.fuzzy_parse_timestamp(new_time)
            pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
            return pub_time
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return response.xpath('//div[@class="tags"]/div/a/text()').extract()

    def get_content_media(self, response) -> list:
        content = []
        img_list = response.xpath('//div[@class="image"]/img')
        for img in img_list:
            img_dict = self.parse_img(response, img)
            content.append(img_dict)
        news_tags = response.xpath(
            '//div[@itemprop="articleBody"]/p/node()|//div[@itemprop="articleBody"]/node()')
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h5", "strong", "span"]:
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
        img_url = urljoin(response.url, news_tag.xpath("./@src").extract_first())
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": img_url}
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
