# -*- coding: utf-8 -*-
import json
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.site_deal.interface_helper import facebook_like_count_interface
from util.time_deal import datetime_helper

"""
    模版
"""


# 列表页 list ->resource/lists/NEWS 列表页全为json数据

class TwPeoplemediaParser(BaseParser):
    name = 'peoplemedia'
    
    # 站点id
    site_id = "d9cda50d-ab86-4220-9d18-227e6e3ee7e3"
    # 站点名
    site_name = "民报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "d9cda50d-ab86-4220-9d18-227e6e3ee7e3", "source_name": "民报", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8c9bd6-fe6f-11ec-a30b-d4619d029786", "专文", "https://www.peoplemedia.tw/resource/lists/NEWS/%E5%B0%88%E6%96%87", "政治"),
            ("4a8c9b68-fe6f-11ec-a30b-d4619d029786", "专栏", "https://www.peoplemedia.tw/resource/lists/CELEBRITY", "政治"),
            ("4a8c9af0-fe6f-11ec-a30b-d4619d029786", "全球", "https://www.peoplemedia.tw/resource/lists/NEWS/%E5%85%A8%E7%90%83", "政治"),
            ("4a8c992e-fe6f-11ec-a30b-d4619d029786", "政治", "https://www.peoplemedia.tw/resource/lists/NEWS/%E6%94%BF%E6%B2%BB", "政治"),
            ("4a8c9c44-fe6f-11ec-a30b-d4619d029786", "论坛", "https://www.peoplemedia.tw/resource/lists/FORUM", "政治"),
            ("4a8c9a46-fe6f-11ec-a30b-d4619d029786", "财经", "https://www.peoplemedia.tw/resource/lists/NEWS/%E8%B2%A1%E7%B6%93", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = json.loads(response.text)
        if news_urls:
            news_urls = news_urls["data_list"]
            for news_url in news_urls:
                yield f"https://www.peoplemedia.tw/news/{news_url['EID']}"

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="news_title"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@itemprop="name"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img = response.xpath('//div[@itemprop="image"]')
        if img:
            con_img = self.parse_img(response, img)
            if con_img:
                content.append(con_img)

        news_tags = response.xpath('//div[@id="newscontent"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)

                if news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip()
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//img/@alt').extract()).strip(),
                   "src": img_url
                   }
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath(".//@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.attrib.get('title'),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag, media_type):
        videoUrl = news_tag.xpath("").extract_first()
        if media_type == "video":
            suffix = ".mp4"
        else:
            suffix = ".mp3"
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }
            return video_dic

    def get_like_count(self, response) -> int:
        like = facebook_like_count_interface(response.url, '//span[@class="_5n6h _2pih"]/text()')
        return like if like else 0

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
