# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import requests
from parsel import Selector

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class HK_crnttParser(BaseParser):
    name = 'hk_crntt'
    
    # 站点id
    site_id = "f6094ee4-655a-4ef7-8e89-a500b77f2a43"
    # 站点名
    site_name = "中国评论新闻网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f6094ee4-655a-4ef7-8e89-a500b77f2a43", "source_name": "中国评论新闻网", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8e3dce-fe6f-11ec-a30b-d4619d029786", "东亚安全", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=218", "政治"),
            ("35f54e38-ad11-11ed-b079-1094bbebe6dc", "两岸综合", "http://www.crntt.com/crn-webapp/coluOutline.jsp?coluid=3", "政治"),
            ("4a8e3e46-fe6f-11ec-a30b-d4619d029786", "中国周报", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=169", "政治"),
            ("e7007b80-7607-11ed-ad4d-d4619d029786", "中国政情", "http://www.crntt.com/crn-webapp/coluOutline.jsp?coluid=151", "政治"),
            ("e700b5c8-7607-11ed-ad4d-d4619d029786", "中国领导人", "http://www.crntt.com/crn-webapp/msgOutline.jsp?coluid=357", "政治"),
            ("4a8e3c02-fe6f-11ec-a30b-d4619d029786", "中评数据", "http://hk.crntt.com/crn-webapp/msgOutline.jsp?coluid=350", "政治"),
            ("4a8e3cfc-fe6f-11ec-a30b-d4619d029786", "中评观察", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=136", "政治"),
            ("4a8e3eb4-fe6f-11ec-a30b-d4619d029786", "军情聚焦", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=4", "政治"),
            ("26f12a41-add6-3727-8e89-5b1d5b532b02", "北台湾网", "http://www.crntt.com/crn-webapp/msgOutline.jsp?coluid=192", "政治"),
            ("391e8dcc-c5d0-4aa9-b5a2-c0556360e3ac", "南台湾讯", "http://www.crntt.com/crn-webapp/msgOutline.jsp?coluid=153", "政治"),
            ("332b482a-ad10-11ed-99c0-1094bbebe6dc", "反腐动向", "http://www.crntt.com/crn-webapp/coluOutline.jsp?coluid=241", "政治"),
            ("4a8e3ca2-fe6f-11ec-a30b-d4619d029786", "台湾时政", "http://hk.crntt.com/crn-webapp/msgOutline.jsp?coluid=46", "政治"),
            ("141b8254-9ecd-5bce-92dd-ef45a2a83f04", "台湾综合", "http://www.crntt.com/crn-webapp/msgOutline.jsp?coluid=217", "政治"),
            ("4a8e3f86-fe6f-11ec-a30b-d4619d029786", "国际时事", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=70", "政治"),
            ("4a8e3c5c-fe6f-11ec-a30b-d4619d029786", "外交纵横", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=202", "政治"),
            ("e7007356-7607-11ed-ad4d-d4619d029786", "大陆新闻", "http://www.crntt.com/crn-webapp/msgOutline.jsp?coluid=45", "政治"),
            ("4a8e3bbc-fe6f-11ec-a30b-d4619d029786", "智库汇聚", "http://hk.crntt.com/crn-webapp/msgOutline.jsp?coluid=266", "政治"),
            ("b0c21fda-7218-11ed-a54c-d4619d029786", "港澳新闻", "http://www.crntt.com/crn-webapp/msgOutline.jsp?coluid=2", "政治"),
            ("4a8e3d6a-fe6f-11ec-a30b-d4619d029786", "经济时评", "http://hk.crntt.com/crn-webapp/msgOutline.jsp?coluid=53", "政治"),
            ("b0c21e0e-7218-11ed-a54c-d4619d029786", "绿营动态", "http://bj.crntt.com/crn-webapp/msgOutline.jsp?coluid=142", "政治"),
            ("4a8e3f18-fe6f-11ec-a30b-d4619d029786", "美国广角", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=148", "政治"),
            ("b0c21db4-7218-11ed-a54c-d4619d029786", "蓝营视点", "http://bj.crntt.com/crn-webapp/msgOutline.jsp?coluid=255", "政治"),
            ("4a8e3ff4-fe6f-11ec-a30b-d4619d029786", "评论世界", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=5", "政治"),
            ("26f12a41-add6-3727-8e89-5b1d5b532b02", "财经科技", "http://www.crntt.com/crn-webapp/coluOutline.jsp?coluid=10", "政治"),
            ("4a8e4062-fe6f-11ec-a30b-d4619d029786", "香港政治", "http://hk.crntt.com/crn-webapp/coluOutline.jsp?coluid=176", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        items = response.xpath("//ul/li")
        if items:
            for item in items:
                news_url = item.xpath("./a/@href").get()
                if not news_url.startswith('http'):
                    news_url = urljoin('http://hk.crntt.com', news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//title/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title.replace("\u3000"," ") or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//tr[3]/td//tr[2]/td/text()[normalize-space()]").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str.lstrip("(").rstrip(")"))
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        news_tags = []

        def parsel_html(url):
            response_url = urljoin(response.url, url)
            html = requests.get(response_url).content.decode("utf-8")
            parser_html = Selector(html)
            news_tags.extend(parser_html.xpath("//td[@id='zoom']/node()"))
            page_next_url = parser_html.xpath(
                "//img[@src='http://hkpic.crntt.com/resource/images/next_page.gif']/parent::a/@href").get()
            if page_next_url:
                parsel_html(page_next_url)

        content = []
        # 存在翻页

        parser_html = Selector(response.text)
        news_tags.extend(
            response.xpath("//td[@id='zoom']/node()|//table[@cellpadding='20']/tbody//table[@align='center']"))
        page_next_url = parser_html.xpath(
            "//img[@src='http://hkpic.crntt.com/resource/images/next_page.gif']/parent::a/@href").get()
        if page_next_url:
            parsel_html(page_next_url)

        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root.strip().replace("\u3000"," "), "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag == "table":
                    if news_tag.xpath(".//img"):
                        img_dic = self.parse_img(response, news_tag, img_xpath=".//img/@src",
                                                 des_xpath=".//tr/td[@align='center']/text()[normalize-space()]")
                        if img_dic:
                            content.append(img_dic)
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
                    new_cons.append(x.replace("\n", "").replace("\r", "").replace('\u3000', '').strip())
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
