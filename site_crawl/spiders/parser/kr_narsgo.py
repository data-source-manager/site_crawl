# -*- coding: utf-8 -*-
import re
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_narsgoParser(BaseParser):
    name = 'kr_narsgo'
    
    # 站点id
    site_id = "f017efdf-4929-4afa-b609-e554d6e8ebb4"
    # 站点名
    site_name = "国会立法调查办公室"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f017efdf-4929-4afa-b609-e554d6e8ebb4", "source_name": "国会立法调查办公室", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91233c9c-2f72-11ed-a768-d4619d029786", "研究报告", "https://www.nars.go.kr/report/list.do?cmsCode=CM0043", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//div[@class='tt']/a/@href").extract() or []
        view_counts = response.xpath("//*[text()[contains(.,'조회수')]]/text()").extract() or []
        if news_urls:
            for index, news_url in enumerate(news_urls):
                formatstr = re.findall("view\('(.*?)'\)", news_url)[0]
                view_count_str = view_counts[index].replace("조회수 : ", "")
                if formatstr:
                    news_url = 'https://www.nars.go.kr/report/view.do?cmsCode=CM0043&brdSeq={}'.format(formatstr)
                self.Dict[news_url] = view_count_str
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h4[@class='vw-ti']/text()").extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        Author_str = response.xpath("//div[@class='zl']/p/span[2]/text()").extract_first()
        if Author_str:
            authors.append(Author_str)
        return authors

    def get_pub_time(self, response) -> str:
        pub = response.xpath("//div[@class='zl']/p/span[1]/text()").extract_first()
        if pub:
            pub = str(datetime_helper.fuzzy_parse_datetime(pub.replace(".", "-")))
            return pub
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 提升作用域

        news_tags = response.xpath("//div[@class='vw-con']/node()|//div[@class='vw-con']/p/node()")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h1", "h2", "h3", "h4", 'h5', "strong"]:
                    if news_tag.xpath(".//img"):
                        img_dict = self.parse_img(response, news_tag)
                        content.append(img_dict)
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
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": response.xpath(".//p/text()").extract_first(),
               "src": img_url
               }
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath(".//a/text()").extract_first(),
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
        read_count = 0
        if self.Dict[response.url]:
            read_count = int(self.Dict[response.url])
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
