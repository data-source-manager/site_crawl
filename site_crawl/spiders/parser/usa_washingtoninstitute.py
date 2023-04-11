# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class USA_washingtoninstituteParser(BaseParser):
    name = 'usa_washingtoninstitute'
    
    # 站点id
    site_id = "bf8b2eb7-b2a4-6d43-4b1f-16f991dcc74c"
    # 站点名
    site_name = "华盛顿近东政策研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "bf8b2eb7-b2a4-6d43-4b1f-16f991dcc74c", "source_name": "华盛顿近东政策研究所", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("544de7ea-43d6-ddf4-752b-7351c31f0761", "专题", "", "政治"),
            ("4a8dfed6-fe6f-11ec-a30b-d4619d029786", "专题/军事与安全", "https://www.washingtoninstitute.org/policy-analysis/military-security", "政治"),
            ("4a8e0002-fe6f-11ec-a30b-d4619d029786", "专题/和平进程", "https://www.washingtoninstitute.org/policy-analysis/peace-process", "政治"),
            ("4a8dfe7c-fe6f-11ec-a30b-d4619d029786", "专题/大国竞争", "https://www.washingtoninstitute.org/policy-analysis/great-power-competition", "政治"),
            ("4a8dff44-fe6f-11ec-a30b-d4619d029786", "专题/美国政策", "https://www.washingtoninstitute.org/policy-analysis/us-policy", "政治"),
            ("4a8dffb2-fe6f-11ec-a30b-d4619d029786", "专题/阿以关系", "https://www.washingtoninstitute.org/policy-analysis/arab-israeli-relations", "政治"),
            ("4a8e0034-fe6f-11ec-a30b-d4619d029786", "新闻稿", "https://www.washingtoninstitute.org/about/press-room/press-release?page=0", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//div[@role='article']/a/@href|//span[@class='field-content link']/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1/span/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_a = response.xpath("//a[@class='link link--ondark font-serif']/text()").get()
        if author_a:
            authors.append(author_a)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath(
            "//div[@class='date pr-8']/text()|//div[@class='flex text-sm items-center mb-10']/text()").get()
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
            "//div[contains(@class,'editorial')]/*|//div[contains(@class,'editorial')]/div[contains(@class,'intro-decoration-horizontal')]/*|//div[contains(@class,'page-header--image')]/article[@class='media image']//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'span']:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["img", 'figure', 'article']:
                    img_src = self.parse_img(response, news_tag, img_xpath="./@src|.//img/@src")
                    if img_src:
                        content.append(img_src)
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
        read_count_str = response.xpath("//span[@class='look']/em/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
