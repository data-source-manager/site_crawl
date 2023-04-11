# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class JP_mojgoParser(BaseParser):
    name = 'jp_mojgo'
    
    # 站点id
    site_id = "17c6b5f9-52f9-fa32-6378-b6bbe94324d1"
    # 站点名
    site_name = "日本出入国在留厅"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "17c6b5f9-52f9-fa32-6378-b6bbe94324d1", "source_name": "日本出入国在留厅", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("3e384be6-a69d-b5f1-f9da-c58d35276d13", "出入境政策", "https://www.moj.go.jp/isa/policies/policies/basic_plan.html", "政治"),
            ("bf88a6d8-9e4d-13cf-4330-3b591f75b3fe", "新闻稿", "https://www.moj.go.jp/isa/publications/press/press2022.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "basic_plan" in response.url:
            self.Dict[response.url] = ""
            yield response.url
        news_urls = response.xpath("//ul[@class='dateList01']/li")
        if news_urls:
            for extrat in news_urls:
                news_url = extrat.xpath("./div[@class='txt']/a/@href").get()
                dates = extrat.xpath("./div[@class='date']/text()").get()
                rsp_url = urljoin(response.url, news_url)
                self.Dict[rsp_url] = dates
                yield rsp_url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='titlePage']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = self.Dict[response.url]
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str.replace("年", "-").replace("月", "-").replace("日", ""))
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='textBlock honbun']/node()|//h2[@class='titleStyle01']")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'span']:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    img_src = self.parse_img(response, news_tag, img_xpath="./@src", des_xpath="./@alt")
                    if img_src:
                        content.append(img_src)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        pdf_files = response.xpath("//ul[@class='arwList01']/li")
        for pdf in pdf_files:
            pdf_file = pdf.xpath("./a/@href").get()
            name = pdf.xpath("./a/text()").get()
            if pdf_file:
                file_dic = {
                    "type": "file",
                    "src": urljoin(response.url, pdf_file),
                    "name": name.strip() or None,
                    "description": None,
                    "md5src": self.get_md5_value(pdf_file) + ".pdf"
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
        read_count_str = response.xpath("//div[@class='infor']/dl[2]/dd/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
