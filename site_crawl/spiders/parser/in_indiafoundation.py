# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class IN_indiafoundationParser(BaseParser):
    name = 'in_indiafoundation'
    
    # 站点id
    site_id = "dc270bf8-ca83-32a9-a2bd-10c7783e9fc7"
    # 站点名
    site_name = "印度基金会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "dc270bf8-ca83-32a9-a2bd-10c7783e9fc7", "source_name": "印度基金会", "direction": "in", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8dfe04-fe6f-11ec-a30b-d4619d029786", "文章和评论", "https://indiafoundation.in/category/articles-and-commentaries/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//h2[@class='entry-title']/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls[:50]:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='entry-title']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_a = response.xpath("//div[@class='writen-by']/text()").get()
        if author_a:
            authors.append(author_a.replace("Written By:", "").strip())
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='archive-date']/text()").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@class='entry-content']/*|//div[@class='trinityAudioPlaceholder']//iframe|//div[@class='if-archive-img']//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'div']:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag == 'img':
                    img_src = self.parse_img(response, news_tag, img_xpath="./@src")
                    if img_src:
                        content.append(img_src)
                elif news_tag.root.tag == "iframe":
                    audio_src = news_tag.xpath("./@src").get()
                    if audio_src:
                        audio_dic = {
                            "type": "video",
                            "src": audio_src,
                            "name": None,
                            "description": None,
                            "md5src": self.get_md5_value(audio_src) + ".mp3"
                        }
                        content.append(audio_dic)
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
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
                   "src": img_url}
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
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
