# -*- coding: utf-8 -*-
import json
import time
from urllib.parse import urljoin

import jsonpath

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class TH_thairathParser(BaseParser):
    name = 'th_thairath'
    
    # 站点id
    site_id = "43b4d11a-da5f-4dc0-b520-8af2f7718933"
    # 站点名
    site_name = "泰国早报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "43b4d11a-da5f-4dc0-b520-8af2f7718933", "source_name": "泰国早报", "direction": "th", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("be61139e-318a-46b8-a364-9621f89a5f07", "国外", "https://www.thairath.co.th/news/foreign", "政治"),
            ("c59a2a47-a8e4-4047-9c4e-eab42064b1bd", "政治", "https://www.thairath.co.th/news/politic", "政治"),
            ("15a744e4-56e7-45d9-b807-4826334099a7", "犯罪", "https://www.thairath.co.th/news/crime", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        date_json = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        date = jsonpath.jsonpath(json.loads(date_json), "$..lastestNews")
        news_urls = jsonpath.jsonpath(date, "$..fullPath")
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="dable:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@property="og:article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_date = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        tag_date = jsonpath.jsonpath(json.loads(tags_date), "$..data")[0]
        tags = jsonpath.jsonpath(tag_date, "$..tags")[0]
        return tags

    def get_content_media(self, response) -> list:
        content = []
        json_date = response.xpath('//script[@class="next-head"][contains(text(),"NewsArticle")]/text()').get()
        imge_date = jsonpath.jsonpath(json.loads(json_date), "$..image")[0]
        for imges in imge_date:
            dic = {
                "type": "image",
                "name": '',
                "md5src": self.get_md5_value(imges) + '.jpg',
                "description": '',
                "src": imges
            }
            content.append(dic)

        contents = jsonpath.jsonpath(json.loads(json_date), "$..articleBody")
        text_dic = {
            "data": contents,
            "type": "text"
        }
        content.append(text_dic)

        return content

    def get_detected_lang(self, response) -> str:
        return "th"

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
        img = news_tag.xpath('./@src').extract_first()
        if img.startswith("data:image/gif;base64"):
            return {}
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//figcaption//text()').extract()).strip(),
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
        return 0

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
