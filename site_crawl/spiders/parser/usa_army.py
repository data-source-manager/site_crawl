# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import requests
import scrapy

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class ArmyParser(BaseParser):
    name = 'army'
    # 站点id
    site_id = "61824cf2-7cef-4d3f-b7f0-9bfdfce8eee5"
    # 站点名
    site_name = "美国陆军"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "61824cf2-7cef-4d3f-b7f0-9bfdfce8eee5", "source_name": "美国陆军", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8bf4d8-fe6f-11ec-a30b-d4619d029786", "军事评论", "https://www.armyupress.army.mil/Journals/Military-Review/English-Edition-Archives/mr-english-2023/", "政治"),
            ("4a8bf3f2-fe6f-11ec-a30b-d4619d029786", "新闻", "https://www.army.mil/news/newsreleases", "政治"),
            ("4a8bf460-fe6f-11ec-a30b-d4619d029786", "陆军全球新闻", "https://www.army.mil/news", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.paoxy = {
            "http": "http://127.0.0.1:9910",
            "https": "http://127.0.0.1:9910"
        }

    def deal(self, urllist) -> list:
        url_list = []
        for url in urllist:
            complete = "https://www.armyupress.army.mil/" + url
            res = scrapy.Selector(text=requests.get(complete).text)
            urls = res.xpath('//p[@class="articletitle"]/a/@href').extract()
            if urls:
                for x in urls:
                    complete_detail_url = "https://www.armyupress.army.mil/" + x
                    url_list.append(complete_detail_url)
        return url_list

    def parse_list(self, response) -> list:
        if "English-Edition-Archives" in response.url:
            news_url = response.xpath('//div[@class="thumbnail"]/a/@href').extract()
            article_url = self.deal(news_url)
            for x in article_url:
                yield x
        else:
            news_urls = response.xpath('//div[@class="headlines"]//li/a/@href|'
                                       '//p[@class="title"]/a/@href').extract() or ""
            if news_urls:
                for news_url in news_urls:
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//title/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//div[@class="span12"]/p/text()').extract_first()
        if authors:
            authors = authors.replace("By", "")
            if authors.strip():
                author_list.append(authors.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//div[@class="span12"]/p/span/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[contains(@class,"article-body")]/div/*|'
                                   '//div[@id="mainContent"]/*|'
                                   '//div[@class="col-sm-8"]/*|//div[@class="col-sm-8"]/div/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    if ".pdf" in news_tag.xpath('./a/@href'):
                        for file in news_tag.xpath('./a'):
                            con_file = self.parse_file(response, file)
                            if con_file:
                                content.append(con_file)
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)

                if news_tag.root.tag == "div":
                    for img in news_tag.xpath('./figure'):
                        con_img = self.parse_img(response, img)
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
                   "description": None,
                   "src": img_url
                   }
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath("./@href").extract_first()
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
