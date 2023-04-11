# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import requests
from parsel import Selector

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class JP_newsgooParser(BaseParser):
    name = 'jp_newsgoo'
    
    # 站点id
    site_id = "47ca7a95-5c8c-5697-2ea0-c8facb5f2ce1"
    # 站点名
    site_name = "日本Goo"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "47ca7a95-5c8c-5697-2ea0-c8facb5f2ce1", "source_name": "日本Goo", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("ac77b726-6142-3937-b124-b7ebec727029", "国际", "", "政治"),
            ("4a8e0bec-fe6f-11ec-a30b-d4619d029786", "国际/科学", "https://news.goo.ne.jp/topstories/backnumber/world/", "政治"),
            ("4a8e0bb0-fe6f-11ec-a30b-d4619d029786", "政治", "https://news.goo.ne.jp/topstories/backnumber/politics/20220520/", "政治"),
            ("4a8e0cfa-fe6f-11ec-a30b-d4619d029786", "社会", "https://news.goo.ne.jp/topstories/backnumber/nation/20220520/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//ul[@class='gn-news-list responsive-margin-bottom']/li/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h2[contains(@class,'topics-title')]//text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//p[@class='topics-news-source margin-bottom15']/text()[normalize-space()][2]").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str.replace(") ", ""))
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='play_cont']/dl/dd/p/node()|//div[@class='play_cont']/dl/dd/strong")
        html_parser = Selector(response.text)
        detail_href = html_parser.xpath("//*[text()[contains(.,'続きを読む')]]/@href").get()
        if detail_href:
            url = urljoin(response.url, detail_href)
            htmls = requests.get(url).text
            select_html = Selector(htmls)
            news_tags = select_html.xpath(
                "//div[@class='clearfix article-text cXenseParse']/node()|//div[@class='article-thumbs']//img")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    img_src = self.parse_img(response, news_tag, img_xpath="./@src", des_xpath="./@alt")
                    if img_src:
                        content.append(img_src)
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
        read_count_str = response.xpath("//*[text()[contains(.,'조회수 :')]]/text()").get()
        if read_count_str:
            read_count = int(read_count_str.replace("조회수 :", ""))
        return read_count

    def get_if_repost(self, response) -> bool:
        if self.Dict.get(response.url):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        repost_source_str = response.xpath("//p[@class='topics-news-source margin-bottom15']/a/text()").get()
        if repost_source_str:
            self.Dict[response.url] = repost_source_str
            repost_source = repost_source_str
        return repost_source
