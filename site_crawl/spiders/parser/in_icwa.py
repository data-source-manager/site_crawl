# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class IN_icwaParser(BaseParser):
    name = 'in_icwa'
    
    # 站点id
    site_id = "c0ca95e4-46b5-4385-9a57-c5ddbb8bbfef"
    # 站点名
    site_name = "印度世界事务所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c0ca95e4-46b5-4385-9a57-c5ddbb8bbfef", "source_name": "印度世界事务所", "direction": "in", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("34af8f40-d4ef-3326-ac78-214c13155bbb", "出版物", "", "政治"),
            ("4a8dc218-fe6f-11ec-a30b-d4619d029786", "出版物/嘉宾专栏", "https://www.icwa.in/show_content.php?lang=1&level=2&ls_id=483&lid=461", "政治"),
            ("4a8dc448-fe6f-11ec-a30b-d4619d029786", "出版物/特别报道", "https://www.icwa.in/show_content.php?lang=1&level=2&ls_id=474&lid=54", "政治"),
            ("4a8dc33a-fe6f-11ec-a30b-d4619d029786", "出版物/观点", "https://www.icwa.in/show_content.php?lang=1&level=2&ls_id=471&lid=53", "政治"),
            ("4a8dc56a-fe6f-11ec-a30b-d4619d029786", "媒体中心", "https://www.icwa.in/show_content.php?lang=1&level=1&ls_id=416&lid=213", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        new_items = response.xpath("//ul[@class='sidebar-links-full']/li")
        if new_items:
            news_url = new_items.xpath("./a/@href").get()
            title = new_items.xpath("./a/text()").get()
            url = urljoin(response.url, news_url)
            self.Dict[url] = title
            yield url

    def get_title(self, response) -> str:
        title = self.Dict[response.url]
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        if "showfile" in response.url or "showlink" in response.url:
            return authors
        author_a = response.xpath("//div[@class='auth_nam_dat']/text()").extract_first()
        if author_a:
            authors.append(author_a.split("|")[0].strip())
        return authors

    def get_pub_time(self, response) -> str:
        if "showfile" in response.url or "showlink" in response.url:
            return "9999-01-01 00:00:00"
        Date_str = response.xpath("//div[@class='auth_nam_dat']/text()").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str.split("|")[-1])
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        if "showfile" in response.url or "showlink" in response.url:
            file_src = response.url
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            content.append(file_dic)
            return content
        news_tags = response.xpath("//div[@class='cms-content']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    if news_tag.xpath(".//img"):
                        img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == 'img':
                    img_src = self.parse_img(response, news_tag, img_xpath="./@src", des_xpath="./@alt")
                    if img_src:
                        content.append(img_src)
                elif news_tag.root.tag == 'iframe':
                    video_src = self.parse_media(response, news_tag)
                    if video_src:
                        content.append(video_src)
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
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
