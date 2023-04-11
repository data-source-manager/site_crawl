# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class MY_isisParser(BaseParser):
    name = 'my_isis'
    
    # 站点id
    site_id = "af9d7142-167a-46b8-8fb7-10b0af1df628"
    # 站点名
    site_name = "马来西亚国际关系与策略研究院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "af9d7142-167a-46b8-8fb7-10b0af1df628", "source_name": "马来西亚国际关系与策略研究院", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8da7c4-fe6f-11ec-a30b-d4619d029786", "出版物", "https://www.isis.org.my/publications/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "video-gallery" in response.url:
            news_items = response.xpath("//div[@class='yottie-widget-video-info']")
            print(news_items)
            for item in news_items:
                url = item.xpath("./a/@href").get()
                title = item.xpath("./a/@title").get()
                date_str = item.xpath("./div[@class='yottie-widget-video-info-passed-time']/text()").get()
                view_str = item.xpath(
                    "./span[@class='yottie-widget-video-info-properties-item'][1]/span[2]/text()").get()
                like_str = item.xpath(
                    "./span[@class='yottie-widget-video-info-properties-item'][1]/span[2]/text()").get()
                self.Dict[url] = {"title": title, "date_str": date_str, "view": view_str, "like": like_str}
                yield urljoin(response.url, url)
        else:

            news_urls = response.xpath(
                "//div[@class='text-center m-2']/a/@href").getall()
            if news_urls:
                for new_url in news_urls:
                    yield urljoin(response.url, new_url)

    def get_title(self, response) -> str:
        if self.Dict.get(response.url):
            return self.Dict[response.url]['title']

        title = response.xpath("//h1[@class='entry-title']/text()").get()
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        if self.Dict.get(response.url):
            return authors
        author_str = response.xpath("//div[@class='td-post-author-name']/a/text()").get()
        if author_str:
            authors.append(author_str)
        return authors

    def get_pub_time(self, response) -> str:
        if self.Dict.get(response.url):
            Date_str = self.Dict[response.url]['date_str']
            if Date_str:
                dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
                return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
            else:
                return "9999-01-01 00:00:00"
        Date_str = response.xpath("//time[@class='entry-date updated td-module-date']/text()").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@class='td-post-content']/*")
        if self.Dict.get(response.url):
            video_src = response.url
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + ".mp4"
            }
            content.append(video_dic)
            return content
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p"] or "ftn" in news_tag.root.get("id",
                                                                                                                  ""):
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag == "iframe":
                    video_src = self.parse_media(response, news_tag)
                    if video_src:
                        content.append(video_src)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        file_src = response.xpath("//*[text()[contains(.,'Read in PDF')]]/parent::a/@href").get()
        if file_src:
            file_src = urljoin(response.url, file_src)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            content.append(file_dic)
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
        like_count = 0
        if self.Dict.get(response.url):
            like_count = int(self.Dict[response.url]['like'].replace("Likes", ""))
        return like_count

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        if self.Dict.get(response.url):
            read_count = int(self.Dict[response.url]['view'].replace("• ", "").replace("Views", ""))
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
