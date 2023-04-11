# -*- coding: utf-8 -*-
# update:(liyun|2023-01-30) -> 新增板块
import re
import time
from urllib.parse import urljoin

import requests
from parsel import Selector

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TH_bangkokpostParser(BaseParser):
    '''
    存在评论
    '''
    name = 'th_bangkokpost'

    # 站点id
    site_id = "abef2910-548e-42e3-8ca0-d1c82ad01b93"
    # 站点名
    site_name = "曼谷邮报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "abef2910-548e-42e3-8ca0-d1c82ad01b93", "source_name": "曼谷邮报", "direction": "th", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d1020-fe6f-11ec-a30b-d4619d029786", "世界", "https://www.bangkokpost.com/world", "其他"),
            ("4a8d1084-fe6f-11ec-a30b-d4619d029786", "商业", "https://www.bangkokpost.com/business/", "经济"),
            ("83be4ad2-4687-4c27-beeb-cdd9388dc771", "财产", "https://www.bangkokpost.com/property/", "经济"),
            ("4a8d0f4e-fe6f-11ec-a30b-d4619d029786", "政治", "https://www.bangkokpost.com/thailand/politics", "政治"),
            ("4a8d0fb2-fe6f-11ec-a30b-d4619d029786", "观点", "https://www.bangkokpost.com/opinion", "政治"),
            ("4a8d10d4-fe6f-11ec-a30b-d4619d029786", "科技", "https://www.bangkokpost.com/tech", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "abef2910-548e-42e3-8ca0-d1c82ad01b93"
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath(
            "//div[@class='listnews-text']/h3/a")
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

        Date_str = response.xpath("//meta[@name='lead:published_at']/@content").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//article/div[@class='box-tag']/ul/li/a/text()").getall()
        if tags:
            for tag in tags:
                tags_list.append(tag.strip())
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[@class='articl-content']/*|//div[@class='box-img']")
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
                elif news_tag.root.tag == "div" and "box-img" in news_tag.root.get("class",
                                                                                   "") or "articlePhotoCenter" in news_tag.root.get(
                    "class", ""):
                    con_img = self.parse_img(response, news_tag, img_xpath=".//img/@src",
                                             des_xpath=".//figcaption/text()|.//p/text()")
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
        url = 'https://www.bangkokpost.com/ajax/_getLikeUnlike.php'
        like_id = re.findall("/(\d+)/", response.url)[0]
        params = {
            "src_id": like_id,
            "status": "99",
            "act": "CONV3"
        }
        res = requests.post(url, data=params)
        if res.status_code == 200:
            html_parser = Selector(res.text)
            like_count_str = html_parser.xpath("//i[@class='icon-like']/parent::a/text()").get()
            if like_count_str:
                like_count = int(like_count_str)
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        comment_count_str = response.xpath("//li[@class='comment-icon']/label/text()").get()
        if comment_count_str:
            comment_count = int(comment_count_str)
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        read_count_str = response.xpath("//div[@class='content']//div[@class='meta']/div[@class='stat']/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""

        return repost_source
