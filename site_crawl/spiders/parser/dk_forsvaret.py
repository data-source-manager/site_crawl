# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import requests
from lxml import etree

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class DK_forsvaretParser(BaseParser):
    name = 'dk_forsvaret'
    
    # 站点id
    site_id = "20429318-463c-4ccc-b8ca-b79c5c8d2382"
    # 站点名
    site_name = "丹麦军队"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "20429318-463c-4ccc-b8ca-b79c5c8d2382", "source_name": "丹麦军队", "direction": "dk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91237248-2f72-11ed-a768-d4619d029786", "消息", "https://www.forsvaret.dk/en/news/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',

        }
        api_url = 'https://www.forsvaret.dk/PageListBlock/UpdateList?sorting=PublishedDescending&root=266%2C0%2C&pagetype=49&authority=266&subjects=&intervals=&mandates=&ongoing=&eventtype=&count=20&pageAuthority=266&cultureInfo=en'
        response = requests.get(api_url, headers=headers)
        html = response.text
        tree_html = etree.HTML(html)
        news_urls = tree_html.xpath("//li[@class='item col-12']/a/@href")
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='mb-3']/text()").get()
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = response.xpath("//span[@class='news-date mt-2 mb-1']/text()").get()
        if datePublished_str:
            dt = datetime_helper.fuzzy_parse_timestamp(datePublished_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='fade-content']/*")
        header_img = response.xpath("//div[@class='col-12'][2]/div[1]/img[@class='img-fluid']/@src").get()
        if header_img:
            header_img_src = urljoin(response.url, header_img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(header_img_src) + '.jpg',
                   "description": response.xpath("//p[@class='image-text mt-2']/text()").get() or None,
                   "src": header_img_src}
            content.append(dic)
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h3", "h5", "span", "p", "blockquote"] and news_tag.root.get("class",
                                                                                                      "") != 'article-meta':
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src", img_des="./@alt")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        """"
            可以对一个标签下存在多个段落进行解析
        """
        dic = {}
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'

        return dic

    def parse_img(self, response, news_tag, img_xpath='', img_des=''):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath(img_xpath).extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(img_des).extract_first() or None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath("./self::a[contains(@href,'.pdf')]/@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.xpath("./self::a[contains(@href,'.pdf')]/text()").get() or None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath(".//iframe/@src").extract_first()
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
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
