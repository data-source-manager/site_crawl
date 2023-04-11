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


class TH_nationnmultimediaParser(BaseParser):
    name = 'th_nationnmultimedia'
    
    # 站点id
    site_id = "7dfd847a-f37e-4193-80a7-58c394cc711b"
    # 站点名
    site_name = "民族报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7dfd847a-f37e-4193-80a7-58c394cc711b", "source_name": "民族报", "direction": "th", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("d47ead10-b9ee-b35b-86b3-bc120de38fd9", "世界", "", "政治"),
            ("bb1c2bad-7516-4d4e-89b7-9ebb2fd2f74c", "世界/东盟", "https://www.nationmultimedia.com/category/world/asean", "政治"),
            ("5550c690-32d8-4cea-a1af-da6a9b61681a", "世界/中国", "https://www.nationmultimedia.com/category/world/china", "政治"),
            ("5ecb8ad6-bfcc-4205-8b31-07d278284c9a", "世界/亚太", "https://www.nationmultimedia.com/category/world/asia-pacific", "政治"),
            ("e0ce2440-477c-4a84-b920-b979806a29b6", "世界/俄罗斯&中亚", "https://www.nationmultimedia.com/category/world/russia-central-asia", "政治"),
            ("d7763641-ec73-4f08-a041-250912e9c769", "世界/欧洲", "https://www.nationmultimedia.com/category/world/europe", "政治"),
            ("f6384b36-77e9-49b2-b329-02386a372bde", "世界/美国&加拿大", "https://www.nationmultimedia.com/category/world/us-canada", "政治"),
            ("fd304857-0b01-4a9f-86b2-d546e71df1d0", "世界/美洲", "https://www.nationmultimedia.com/category/world/americas", "政治"),
            ("c8f0a6e2-4625-566c-5960-91cc0eb64583", "泰国", "", "政治"),
            ("4dd4e830-a06a-40b4-84a7-30d891c53ef7", "泰国/政治", "https://www.nationmultimedia.com/category/thailand/politics", "政治"),
            ("c35065b9-e18d-4a09-bc46-c6e9ed975697", "泰国/政策", "https://www.nationmultimedia.com/category/thailand/policies", "政治"),
            ("c3711948-cde2-4372-a253-5af2401ba7c1", "泰国/经济", "https://www.nationmultimedia.com/category/thailand/economy", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        date_json = response.xpath('//script[@id="__NEXT_DATA__"]/text()').get()
        date = jsonpath.jsonpath(json.loads(date_json), "$..articles")
        news_urls = jsonpath.jsonpath(date, "$..link")
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="card-title line-clamp --2"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

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
        tags_list = []

        tags = response.xpath('//div[@class="tags-wrapper"]/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath(
            '//div[@class="get-image__ResolutionWrapper-sc-y8v0u4-0 dpiaMY resolution-image"]//img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//div[@class="content-detail"]//img|//div[@class="content-detail"]/*')
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
