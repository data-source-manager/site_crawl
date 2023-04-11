# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Usa_amlcarmyParser(BaseParser):
    name = 'usa_amlcarmy'
    # 站点id
    site_id = "78f22d2e-7b01-4e9e-bf1d-762aedf76eee"
    # 站点名
    site_name = "陆军医疗后勤司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "78f22d2e-7b01-4e9e-bf1d-762aedf76eee", "source_name": "陆军医疗后勤司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("b5e6d1ea-c504-4491-a763-880805fb9298", "USAMMC-E新闻", "https://www.amlc.army.mil/USAMMC-E/", "政治"),
            ("6259d057-156f-41bd-a7ff-f93605173323", "USAMMC-K新闻", "https://www.amlc.army.mil/USAMMC-K/", "政治"),
            ("91231a82-2f72-11ed-a768-d4619d029786", "消息", "https://www.amlc.army.mil/News/", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//span[@id='linkTitle']/a/@href").extract() or ""
        if news_urls:
            for news_url in (news_urls):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='span12']/h1/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        author = []
        authors = response.xpath("//div[@class='span12']/p[@class='small']/text()").extract_first() or ""
        if authors:
            author.append(authors.replace("By", "").strip())
        return author

    def get_pub_time(self, response) -> str:

        time_str = response.xpath("//p[@class='small']/span/text()").extract_first() or ""
        dt_ = datetime_helper.fuzzy_parse_timestamp(time_str)
        if dt_:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath("//a[@class='domain-label']/text()").extract()
        return [tags for tags in tags_node]

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='ql-editor']/*|//div[@class='ql-editor']//figure")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == 'figure':
                    img_dict = self.parse_img(response, news_tag, xpath_src=".//img/@src",
                                              xpath_des=".//span[@class='caption-text']/text()")
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
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
                if "延伸閱讀" in x.strip():
                    continue
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
