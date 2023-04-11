# -*- coding: utf-8 -*-
import json
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class FrRfiCnParser(BaseParser):
    name = 'rfi'
    
    # 站点id
    site_id = "8fa19fa5-cbf3-458b-ae5a-b6bc936ae52d"
    # 站点名
    site_name = "法国国际广播电台"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "8fa19fa5-cbf3-458b-ae5a-b6bc936ae52d", "source_name": "法国国际广播电台", "direction": "fr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b406a-fe6f-11ec-a30b-d4619d029786", "中东", "https://www.rfi.fr/cn/%E4%B8%AD%E4%B8%9C/", "政治"),
            ("4a8b4182-fe6f-11ec-a30b-d4619d029786", "中国", "https://www.rfi.fr/cn/%E4%B8%AD%E5%9B%BD/", "政治"),
            ("a7161054-990c-4152-8730-4b2f54d1f236", "乌克兰危机", "https://www.rfi.fr/cn/%E5%85%B3%E9%94%AE%E8%AF%8D/%E4%B9%8C%E5%85%8B%E5%85%B0%E5%8D%B1%E6%9C%BA/", "政治"),
            ("846e4481-dbca-40c0-884b-a63a9311ac17", "亚洲", "https://www.rfi.fr/cn/%E4%BA%9A%E6%B4%B2/", "政治"),
            ("7ab5fdb9-df20-475d-a31f-8b00c00b8be9", "政治", "https://www.rfi.fr/cn/%E6%94%BF%E6%B2%BB/", "政治"),
            ("4a8b401a-fe6f-11ec-a30b-d4619d029786", "欧洲", "https://www.rfi.fr/cn/%E6%AC%A7%E6%B4%B2/", "政治"),
            ("4a8b4132-fe6f-11ec-a30b-d4619d029786", "港澳台", "https://www.rfi.fr/cn/%E6%B8%AF%E6%BE%B3%E5%8F%B0/", "政治"),
            ("4a8b3f7a-fe6f-11ec-a30b-d4619d029786", "美洲", "https://www.rfi.fr/cn/%E7%BE%8E%E6%B4%B2/", "政治"),
            ("4a8b3f20-fe6f-11ec-a30b-d4619d029786", "非洲", "https://www.rfi.fr/cn/%E9%9D%9E%E6%B4%B2/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[contains(@class,"m-item-list-article")]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[contains(@class,"a-page-title")]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//a[@class="m-from-author__name"]/@title').extract()
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
        tags_list = []

        tags = response.xpath('//ul[@class="m-tags-list"]/li/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        video = response.xpath('//button[@class="m-feed-sub__audio"]/script/text()').extract_first()
        if video:
            json_data = json.loads(video.strip())["sources"][0]["url"]
            if json_data:
                dic = {"type": "video",
                       "name": None,
                       "md5src": self.get_md5_value(json_data) + '.mp3',
                       "description": None,
                       "src": json_data
                       }
                content.append(dic)
        video = response.xpath('//div[@class="t-content__main-media"]//video-player/@source').extract_first()
        if video:
            video_dic = {
                "type": "video",
                "src": video,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video) + ".mp4"
            }
            content.append(video_dic)
        img_list = response.xpath('//div[@class="t-content__main-media"]/figure')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))

        news_tags = response.xpath('//div[contains(@class,"t-content__body")]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

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
        img = news_tag.xpath('.//img/@srcset').extract_first()
        if img:
            if "," in img:
                img = img.split(",")[0].split(" ")[0].strip()
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath("./figcaption//text()").extract()).strip(),
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
