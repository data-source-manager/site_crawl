# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Tw_nccueduParser(BaseParser):
    name = 'tw_nccuedu'
    
    # 站点id
    site_id = "7bc58c0b-046a-4494-80d8-f6c940f1614f"
    # 站点名
    site_name = "台湾国立政治大学国际关系研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7bc58c0b-046a-4494-80d8-f6c940f1614f", "source_name": "台湾国立政治大学国际关系研究中心", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9123129e-2f72-11ed-a768-d4619d029786", "最新消息", "https://iir.nccu.edu.tw/PageDoc?fid=7477", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//ul[@class='page-list-cont']/li//a/@href").extract() or ""
        view_count_list = response.xpath(
            "//ul[@class='page-list-cont']/li//div[@class='browse-num']/span/text()").extract() or []
        if news_urls:
            for index, news_url in enumerate(news_urls):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                self.Dict[news_url] = view_count_list[index]
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h2[@class='unit-title']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        author = []
        author_str = response.xpath(
            "//*[text()[contains(.,'聯絡電話：')]]/following-sibling::span[last()]/text()").extract_first(
            default="") or ""
        if author_str:
            author.append(author_str)
        return author

    def get_pub_time(self, response) -> str:

        time_str = response.xpath("//div[@class='page-date']//text()[normalize-space()]").extract_first() or ""
        time_str = time_str.replace("日期：", "")
        dt_ = datetime_helper.fuzzy_parse_timestamp(time_str)
        if dt_:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        pass

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//section[@class='DocContent']/*|//div[@class='page-slider page-slider-for']//img|//div[@class='FloatCenterImg']//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == 'img':
                    img_dict = self.parse_img(response, news_tag, xpath_src="./@src", xpath_des="./@alt")
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
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

    def parse_img(self, response, news_tag, xpath_src='', xpath_des=''):
        if xpath_src:
            img_url = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(xpath_des).extract_first() if xpath_des else None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("//a[@class='entry_file_link']/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath("//h2[@class='aside_h2']/text()").extract_first(),
            "description": news_tag.xpath("//h3[@class='entry_title entry_title__file']/text()").extract_first(),
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag, xpath_src='', xpath_des=''):
        video_src = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": news_tag.xpath(xpath_des).extract_first(),
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
        return int(self.Dict[response.url])

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
