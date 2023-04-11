# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class MY_sinchewParser(BaseParser):
    name = 'my_sinchew'
    
    # 站点id
    site_id = "9eccab0f-b17b-41a3-be39-f7cdacacb80a"
    # 站点名
    site_name = "星洲日报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "9eccab0f-b17b-41a3-be39-f7cdacacb80a", "source_name": "星洲日报", "direction": "my", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f2b5793d-94de-3ffa-85a8-5a5439357424", "国内", "", "政治"),
            ("4a8d0706-fe6f-11ec-a30b-d4619d029786", "国内/2021大选", "https://www.sinchew.com.my/category/%e5%85%a8%e5%9b%bd/%e5%85%a8%e5%9b%bd%e5%a4%a7%e9%80%892021/", "政治"),
            ("4a8d05b2-fe6f-11ec-a30b-d4619d029786", "国内/政治", "https://www.sinchew.com.my/category/%e5%85%a8%e5%9b%bd/%e6%94%bf%e6%b2%bb/", "政治"),
            ("ed0bdb35-5d99-3f28-a1a5-d51dbc0e5318", "国际", "", "政治"),
            ("4a8d0850-fe6f-11ec-a30b-d4619d029786", "国际/即时国际", "https://www.sinchew.com.my/category/%e5%9b%bd%e9%99%85/%e5%8d%b3%e6%97%b6%e5%9b%bd%e9%99%85/", "政治"),
            ("4a8d0526-fe6f-11ec-a30b-d4619d029786", "头条", "https://www.sinchew.com.my/category/%e5%a4%b4%e6%9d%a1/", "政治"),
            ("e6220091-cd33-3fd9-92bb-dd9ed8c9553c", "言路", "", "政治"),
            ("4a8d09a4-fe6f-11ec-a30b-d4619d029786", "言路/风雨看潮生", "https://www.sinchew.com.my/category/%e8%a8%80%e8%b7%af/%e9%a3%8e%e9%9b%a8%e7%9c%8b%e6%bd%ae%e7%94%9f/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath(
            "//div[@class='title']/a[@class='internalLink']")
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
        auhtor_strs = response.xpath("//p[@class='xg1']/a/text()").get()
        if auhtor_strs:
            authors.append(auhtor_strs)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='article-page-date']//span[2]/text()").getall()
        if Date_str:
            dates = " ".join(Date_str)
            mn, day, mt, year = re.findall("([\s\S]+) (\d{1,2}).(\d{1,2}).(\d{4})", dates)[0]
            dt = year + "-" + mt + "-" + day + " " + mn
            dt_ = datetime_helper.fuzzy_parse_timestamp(dt)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//a[@class='internalLink']/span/text()").getall()
        if tags:
            tags = list(set(tags))
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[@itemprop='articleBody']/node()|//div[@itemprop='articleBody']/div[@class='mceTemp']/node()|//div[@class='qubely-testimonial-content']/div/node()")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h4", "h5", "span", "p", "blockquote"]:
                    if news_tag.xpath(".//img"):
                        img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src", des_xpath=".//img/@alt")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["img", "figure"]:
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src|.//img/@src",
                                             des_xpath=".//figcaption[@class='wp-caption-text']/text()")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        if text_dict:
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
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        read_count_str = response.xpath("//span[contains(@class,'post-view-counter')]/text()").get()
        if read_count_str:
            read_count = int(read_count_str.replace("点阅", ""))
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
