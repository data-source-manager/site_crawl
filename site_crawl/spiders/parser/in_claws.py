# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from util.site_deal import interface_helper
from .base_parser import BaseParser


class IN_clawsParser(BaseParser):
    name = 'in_claws'

    # 站点id
    site_id = "270e4277-81fc-49b6-b159-04712a3c7553"
    # 站点名
    site_name = "地面作战研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "270e4277-81fc-49b6-b159-04712a3c7553", "source_name": "地面作战研究中心", "direction": "in",
               "if_front_position": False},
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("a9c818be-2037-449a-bb04-73ed1e766581", "出版物", "https://carnegie.ru/publications/", "政治"),
            ("befecb44-ffcc-4063-8aa9-b4e7cb27bba7", "文章", "https://www.claws.in/articles/", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@class='item-details']/h3[@class='entry-title td-module-title']/a/@href|"
                                   "//ul[contains(@class,'clean-list')]/li/h4/a/@href").extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="") or ""
        return title.strip() or ""

    def get_author(self, response) -> list:
        author = response.xpath('//meta[@name="author"]/@content').extract()
        return author

    def get_pub_time(self, response) -> str:
        # 7 luglio 2022
        time_ = response.xpath('//div[contains(@class,"smaller-text")]/text()').extract_first()
        if time_:
            return str(datetime.strptime(time_, "%d.%m.%Y"))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath("//ul[@class='td-tags td-post-small-box clearfix']/li//text()")
        return [tags.strip() for tags in tags_node]

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='article-body']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    if news_tag.xpath(".//a[contains(@href,'pdf')]/@href"):
                        file_dict = self.parse_file(response, news_tag)
                        content.append(file_dict)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
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
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//a[contains(@href,'pdf')]/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": news_tag.xpath(".//a[contains(@href,'pdf')]/text()").extract_first(),
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url, news_tag.xpath("").extract_first())
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
        like_count_str = interface_helper.request_interface(
            "//*[text()[contains(.,'赞')]]/following-sibling::span/text()", response.url)
        if like_count_str:
            like_count = int(like_count_str)
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        comment_count_str = response.xpath("//div[@class='td-post-comments']//text()")
        if comment_count_str:
            comment_count = int(comment_count_str)
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        read_count_str = response.xpath(
            "//div[@class='td-post-views']/span[contains(@class,'td-nr-views-')]/text()").extract_first()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
