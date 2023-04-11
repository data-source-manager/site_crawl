# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class IN_delhipolicygroupParser(BaseParser):
    name = 'in_delhipolicygroup'

    # 站点id
    site_id = "159a6e57-cc96-4a14-a558-4ecbfece448c"
    # 站点名
    site_name = "德里政策集团"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "159a6e57-cc96-4a14-a558-4ecbfece448c", "source_name": "德里政策集团", "direction": "in", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块主题)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("d702ba6a-516d-36f3-bb3c-3b7e7eb6a250", "研究", "", "政治"),
            ("4a8dbd9a-fe6f-11ec-a30b-d4619d029786", "研究/政策报告", "https://www.delhipolicygroup.org/publication/policy-reports.html", "政治"),
            ("4a8dbebc-fe6f-11ec-a30b-d4619d029786", "研究/政策简报", "https://www.delhipolicygroup.org/publication/policy-briefs.html", "政治"),
            ("4a8dbfca-fe6f-11ec-a30b-d4619d029786", "国际期刊", "https://www.delhipolicygroup.org/publication/international-journals.html?page=1", "政治"),
        ]
    ]


    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath(
            "//div[@class='media-body']")
        if news_items:
            for item in news_items:
                url = item.xpath("./a/@href").get()
                title = item.xpath("./a/@alt").get()
                date_str = item.xpath("./span[1]/text()").get()
                authors_str = item.xpath("./span[@class='name-plate']/a/text()").getall()
                rsp_url = urljoin(response.url, url)
                self.Dict[rsp_url] = {"title": title, "date_str": date_str.replace("Date:", ""), "author": authors_str}
                yield rsp_url

    def get_title(self, response) -> str:
        title = self.Dict[response.url]['title']
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_Str = self.Dict[response.url]['author']
        if author_Str:
            authors.extend(author_Str)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = self.Dict[response.url]['date_str']
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
            "//h1/following-sibling::node()|//div[contains(@id,'ftn')]|//div[@class='swiper-slide']//img")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p"] or "ftn" in news_tag.root.get(
                        "id", ""):
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        file_src = response.xpath(
            "//*[text()[contains(.,' View Download')]]/parent::div/a/@href|//*[text()[contains(.,'Download ')]]/parent::div/a/@href").get()
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
