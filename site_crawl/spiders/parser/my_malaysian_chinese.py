# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from lxml import etree

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class MY_malaysian_chineseParser(BaseParser):
    name = 'my_malaysian_chinese'
    
    # 站点id
    site_id = "5c3a6a0a-5501-11ed-aedc-6030d461e866"
    # 站点名
    site_name = "华社研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "5c3a6a0a-5501-11ed-aedc-6030d461e866", "source_name": "华社研究中心", "direction": "my", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("ea0c4b17-83a8-dc6a-22e3-7332ea2cf1e8", "新闻动态", "", "政治"),
            ("6062f3b3-06bc-461c-830d-35131edbe563", "新闻动态/新闻", "http://www.malaysian-chinese.net/newsevents/news/index.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@class='col-12']/li/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h3/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//span[@class='info_text']/text()").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str.replace("时间：", "").replace("来源：", "").strip())
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@id='news_sub_header']/following-sibling::div[@class='container']//div[@class='col-12']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'div']:
                    if news_tag.xpath(".//img"):
                        img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag in "table":
                    html_str = etree.tostring(news_tag.root, encoding="utf-8").decode("utf-8")
                    content.append({'data': html_str, 'type': 'text'})
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
