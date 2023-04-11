# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class HK_mingpaoParser(BaseParser):
    name = 'hk_mingpao'
    
    # 站点id
    site_id = "03554f08-8aef-4a78-9fe4-c30f6db3ceb4"
    # 站点名
    site_name = "明报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "03554f08-8aef-4a78-9fe4-c30f6db3ceb4", "source_name": "明报", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8da706-fe6f-11ec-a30b-d4619d029786", "两岸", "https://news.mingpao.com/ins/%E5%85%A9%E5%B2%B8/section/20220518/s00004", "政治"),
            ("4a8da756-fe6f-11ec-a30b-d4619d029786", "国际", "https://news.mingpao.com/ins/%E5%9C%8B%E9%9A%9B/section/20220518/s00005", "政治"),
            ("4a8da68e-fe6f-11ec-a30b-d4619d029786", "港闻", "https://news.mingpao.com/pns/%E6%B8%AF%E8%81%9E/section/20221116/s00002", "政治"),
            ("b0c221c4-7218-11ed-a54c-d4619d029786", "社评", "https://news.mingpao.com/pns/%E7%A4%BE%E8%A9%95/section/20221116/s00003", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//ul[@class='twocol left']/li[@class='list1']/a/@href|"
                                   "//div[@class='inontent']/a/@href|//div[@class='listing']/ul/li/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin("https://news.mingpao.com/", news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//div[@id='blockcontent']/hgroup/h1/text()").get()
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='date']/text()").get()
        if Date_str:
            year, mt, day = re.findall("(\d{4})年(\d{1,2})月(\d{1,2})日", Date_str)[0]
            dt_ = year + "-" + mt + "-" + day
            dt = datetime_helper.fuzzy_parse_timestamp(dt_)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@id='lower']/p/a[@class='color6th']/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@id='upper']/*|//div[@id='zoomedimg']//img|//div[@class='articlelogin']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@data-original", des_xpath="./@alt")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        file_src = response.xpath("//*[text()[contains(.,'Read in PDF')]]/parent::a/@href").get()
        if file_src:
            file_src = urljoin(response.url, file_src)
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
        like_count = 0
        if self.Dict.get(response.url):
            like_count = int(self.Dict[response.url]['like'].replace("Likes", ""))
        return like_count

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        if self.Dict.get(response.url):
            read_count = int(self.Dict[response.url]['view'].replace("• ", "").replace("Views", ""))
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
