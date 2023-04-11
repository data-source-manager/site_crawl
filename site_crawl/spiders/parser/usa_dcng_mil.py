# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class DcngmilParser(BaseParser):
    name = 'dcngmil'
    
    # 站点id
    site_id = "8ec14bf3-7438-4822-ba87-6a04d6e0c634"
    # 站点名
    site_name = "哥伦比亚特区陆军国民警卫队"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "8ec14bf3-7438-4822-ba87-6a04d6e0c634", "source_name": "哥伦比亚特区陆军国民警卫队", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f2315924-8cde-351a-b180-04eb9af5c60d", "公共事务", "", "政治"),
            ("91231cd0-2f72-11ed-a768-d4619d029786", "公共事务/新闻发布", "https://dc.ng.mil/Public-Affairs/News-Release/", "军事"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.urltimedict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//span[@class="title"]/a/@href').extract()
        for news in news_urls:
            yield urljoin(response.url, news)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="title"]/text()').extract_first(default="") or ""
        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        new_time = response.xpath('//div[@class="category-date"]/text()[2]').extract_first(default="")
        if new_time:
            try:
                new_time = new_time.replace('|', '').strip()
                pub_time = datetime_helper.fuzzy_parse_timestamp(new_time)
                pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
                return pub_time
            except:
                print('时间提取出错')
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('//div[@class="image"]/img|'
                                   '//div[@class="body"]/p/img|'
                                   '//div[@class="body"]/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                if news_tag.root.tag in ["p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "en"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if "_____" in x:
                    continue
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('alt'),
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
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
