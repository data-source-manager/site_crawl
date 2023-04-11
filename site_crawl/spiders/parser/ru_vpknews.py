# -*- coding: utf-8 -*-
import json
import os
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class RU_vpknewsParser(BaseParser):
    '''
    存在评论
    '''
    name = 'ru_vpknews'
    
    # 站点id
    site_id = "0e6dd6db-d8c2-43f3-8200-be731af89eca"
    # 站点名
    site_name = "军工速递周刊"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "0e6dd6db-d8c2-43f3-8200-be731af89eca", "source_name": "军工速递周刊", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d120a-fe6f-11ec-a30b-d4619d029786", "军队", "https://vpk-news.ru/rubric/4", "政治"),
            ("4a8d11d8-fe6f-11ec-a30b-d4619d029786", "地缘政治", "https://vpk-news.ru/rubric/2", "政治"),
            ("4a8d1340-fe6f-11ec-a30b-d4619d029786", "故事", "https://vpk-news.ru/rubric/9", "政治"),
            ("4a8d13a4-fe6f-11ec-a30b-d4619d029786", "概念", "https://vpk-news.ru/rubric/8", "政治"),
            ("4a8d12d2-fe6f-11ec-a30b-d4619d029786", "武器", "https://vpk-news.ru/rubric/12", "政治"),
            ("4a8d1264-fe6f-11ec-a30b-d4619d029786", "防御", "https://vpk-news.ru/rubric/5", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath(
            "//div[@class='topic-news-item-title']/a")
        if news_items:
            for item in news_items:
                news_url = item.xpath("./@href").get()
                title = item.xpath("./text()").get()
                rsp_url = urljoin(response.url, news_url)
                self.Dict[rsp_url] = title
                yield rsp_url

    def get_title(self, response) -> str:
        title = self.Dict[response.url]
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        auhtor_strs = response.xpath("//div[@class='author']/a/text()").get()
        if auhtor_strs:
            authors.append(auhtor_strs)
        return authors

    def get_pub_time(self, response) -> str:

        Date_str = response.xpath("//div[@class='author-post-date']/text()").get()
        if Date_str:
            path_file = os.path.abspath(os.path.join(os.path.abspath(__file__), "../../../../"))
            json_file = os.path.join(path_file, "resource/language/ru.json")
            month = Date_str.split(" ")[1]
            with open(json_file, 'r') as json_fp:
                transport = json.load(json_fp)
                mt = transport[month]
            time_str = Date_str.replace(month, mt)
            dt = datetime_helper.fuzzy_parse_timestamp(time_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//p[@class='tags']/a/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[contains(@class,'post-content')]/*|//div[@class='post-descr']/*|//div[@class='author-post-img']/img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p", "blockquote"]:
                    if news_tag.xpath(".//img"):
                        img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src", des_xpath=".//img/@alt")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        file_src = response.xpath("//a[contains(@class,'dk-article__download')]/@href").get()
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
        video_src = news_tag.xpath("./source/@src").extract_first()
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(video_src) + ".mp4"
        }
        return video_dic

    def get_like_count(self, response) -> int:
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        read_count_str = response.xpath("//div[@class='content']//div[@class='meta']/div[@class='stat']/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        if self.Dict.get(response.url):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        repost_source_str = response.xpath("//*[text()[contains(.,'Источник')]]/em/a/text()").get()
        if repost_source_str:
            self.Dict[response.url] = repost_source_str
            repost_source = repost_source_str
        return repost_source
