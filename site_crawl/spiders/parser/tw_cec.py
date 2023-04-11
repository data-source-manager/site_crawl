# -*- coding: utf-8 -*-
import json
from urllib.parse import urljoin

import scrapy

from site_crawl.spiders.parser.base_parser import BaseParser

"""
    站点解析模版
"""


class TwCecParser(BaseParser):
    name = 'cec'
    
    # 站点id
    site_id = "7e3ffd12-6c70-48f6-b4e8-b10188d92437"
    # 站点名
    site_name = "中央选举委员会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7e3ffd12-6c70-48f6-b4e8-b10188d92437", "source_name": "中央选举委员会", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("b0c21b20-7218-11ed-a54c-d4619d029786", "最新消息", "https://www.cec.gov.tw/data/contentJson/news.json", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.deatil = {}

    def parse_list(self, response) -> list:
        news_urls = json.loads(response.text)["topList"][0:100]
        if news_urls:
            for news_url in news_urls:
                url = f'https://www.cec.gov.tw/article/content/?id=M0010&target=%2Farticle%2F{news_url["id"]}'
                real_url = f'https://www.cec.gov.tw/data/contentJson/article/{news_url["id"]}.json'
                self.deatil[real_url] = {
                    "pub": news_url["begTime"],
                    "title": news_url["title"]
                }
                yield {
                    "real_url": real_url,
                    "origin_url": url
                }

    def get_title(self, response) -> str:
        title = self.deatil[response.url]["title"]
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_str = self.deatil[response.url]["pub"]
        if time_str:
            return f'{time_str[0:4]}-{time_str[4:6]}-{time_str[6:8]} {time_str[8:10]}:{time_str[10:12]}:{time_str[12:14]}'

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return json.loads(response.text).get("tag")

    def get_content_media(self, response) -> list:
        content = []

        con_json = json.loads(response.text)
        news_tags = scrapy.Selector(text=con_json["content"]).xpath("//p|//figure")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)

                if news_tag.root.tag == "figure":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)
        file_list = con_json["fileList"]
        if file_list:
            for file in file_list:
                file_url = urljoin(response.url, file["url"])
                file_dic = {
                    "type": "file",
                    "src": file_url,
                    "name": file["name"],
                    "description": None,
                    "md5src": file["hash"] + ".pdf"
                }
                content.append(file_dic)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        dic = {}
        if cons:
            for con in cons:
                if con:
                    dic['data'] = "".join(con).strip()
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
            if img.startswith("data:image/gif;base64"):
                return {}
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
        videoUrl = news_tag.xpath("./@src").extract_first()
        suffix = f".{media_type}"

        video_dic = {}

        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }

            if suffix == ".mp3":
                video_dic["type"] = "audio"
            elif suffix == ".mp4":
                video_dic["type"] = "video"

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
        return response.xpath('//span[@class="articleOrg"]/text()').extract_first()
