# -*- coding: utf-8 -*-
import json
import time
from urllib.parse import urljoin

import requests

from site_crawl.spiders.parser.base_parser import BaseParser

"""
    模版
"""


class JpNhkParser(BaseParser):
    name = 'nhk'
    
    # 站点id
    site_id = "be967227-24e9-49c3-b355-f0d8c4c1d67d"
    # 站点名
    site_name = "日本广播协会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "be967227-24e9-49c3-b355-f0d8c4c1d67d", "source_name": "日本广播协会", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b9c7c-fe6f-11ec-a30b-d4619d029786", "新闻一览", "https://www3.nhk.or.jp/nhkworld/zh/news/list/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.img = {}
        self.alt = {}
        self.date = {}

    def parse_list(self, response) -> list:
        json_url = "https://nwapi.nhk.jp/nhkworld/rdnewsweb/v7b/zh/outline/list.json"
        res = json.loads(requests.get(json_url).text)["data"]
        if res:
            for x in res:
                url = urljoin(response.url, x["page_url"])
                header_img = x.get("thumbnails")
                if header_img:
                    img_url = header_img.get("middle")
                    alt = header_img.get('alt')
                    self.img[url] = img_url
                    self.alt[url] = alt
                pub = x.get('updated_at')
                if pub:
                    self.date[url] = pub
                yield url
        # yield "https://www3.nhk.or.jp/nhkworld/zh/news/385025/"

    def get_title(self, response) -> str:
        title = response.xpath('//h1/span/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = self.date.get(response.url)
        if time_:
            time_ = time.localtime(1662362311)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time_))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img = self.img.get(response.url)
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": self.alt[response.url],
                   "src": img_url
                   }
            content.append(dic)
        news_tags = response.xpath('//div[@class="p-article__body"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)

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
        img = news_tag.xpath('./@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('./@alt').extract()).strip(),
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

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("").extract_first()
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
