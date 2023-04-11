# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class RU_nvongParser(BaseParser):
    name = 'ru_nvong'
    
    # 站点id
    site_id = "9af43cf8-a76d-4e06-b8d3-d20253499c62"
    # 站点名
    site_name = "独立军事观察报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "9af43cf8-a76d-4e06-b8d3-d20253499c62", "source_name": "独立军事观察报", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("5f4f8b49-2a7a-e385-eef6-45c9a14631a4", "专题", "", "政治"),
            ("4a8d1962-fe6f-11ec-a30b-d4619d029786", "专题/政治", "https://www.ng.ru/politics/", "政治"),
            ("4a8d18ea-fe6f-11ec-a30b-d4619d029786", "专题/社论", "https://www.ng.ru/editorial/", "政治"),
            ("4a8d187c-fe6f-11ec-a30b-d4619d029786", "报纸", "https://nvo.ng.ru/gazeta/", "政治"),
            ("4a8d17fa-fe6f-11ec-a30b-d4619d029786", "消息", "https://nvo.ng.ru/news/index.php?PAGEN_1=1", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//dl[@class='datelist']/dd/a/@href|//div[@class='content']//h3/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='htitle black']/text()").get()
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        auhtor_strs = response.xpath("//p[@class='author']/a/text()[normalize-space()]").get()
        if auhtor_strs:
            authors.append(auhtor_strs)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//p[@class='info']/span[1]/text()|//p[@class='info']/span[2]/text()").getall()
        if Date_str:
            try:
                mn, day, mt, year = re.findall("([\s\S]+) (\d{1,2}).(\d{1,2}).(\d{4})", " ".join(Date_str))[0]
                dt_ = year + "-" + mt + "-" + day + " " + mn
                dt = datetime_helper.fuzzy_parse_timestamp(dt_)
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
            except:
                day, mt, year, mn = re.findall("(\d{1,2}).(\d{1,2}).(\d{4}) ([\s\S]+)", " ".join(Date_str))[0]
                dt_ = year + "-" + mt + "-" + day + " " + mn
                dt = datetime_helper.fuzzy_parse_timestamp(dt_)
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
            "//article[@class='typical']/node()|//div[@class='w700']/hr/following-sibling::p")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span",
                                           "p"] or "k-article__quote-text" in news_tag.root.get("class", ""):
                    if news_tag.xpath(".//img"):
                        img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src",
                                                 des_xpath=".//span[@class='descrPhoto']/text()")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "table" and "ImgDescription" in news_tag.root.get("class", ""):
                    con_img = self.parse_img(response, news_tag, img_xpath=".//tr[1]//img/@src",
                                             des_xpath=".//tr[2]//text()")
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
