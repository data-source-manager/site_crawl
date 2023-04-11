# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class USA_tobyhannaParser(BaseParser):
    name = 'usa_tobyhanna'
    
    # 站点id
    site_id = "02a4e9f9-b563-451d-9fed-52e5127be994"
    # 站点名
    site_name = "美国托比汉纳陆军仓库"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "02a4e9f9-b563-451d-9fed-52e5127be994", "source_name": "美国托比汉纳陆军仓库", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("30804b16-fd76-3b7c-b549-c47ff292dff2", "媒体", "", "政治"),
            ("912338c8-2f72-11ed-a768-d4619d029786", "媒体/消息", "https://www.tobyhanna.army.mil/Media/News/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.urltimedict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//span[@id='linkTitle']/a/@href").extract() or []
        if news_urls:
            for news in news_urls:
                url = urljoin(response.url, news)
                yield url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='title']/text()").extract_first(default="") or ""

        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        author_str = response.xpath("//p[@class='info']/span[@class='line']/text()").extract_first()
        if author_str.strip():
            author_a = author_str.replace("By", "")
            for author in author_a.split("and"):
                authors.append(author)
        else:
            return authors

    def get_pub_time(self, response) -> str:
        # Wednesday, January 5, 2022 9:37:00
        new_time = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if new_time:
            return str(datetime_helper.fuzzy_parse_datetime(new_time))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags = response.xpath('//span[@class="blogtags"]/a/text()').extract()
        if tags:
            return tags
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('//div[@itemprop="articleBody"]/*|//div[@class="item"]//img')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    if img_dict:
                        content.append(img_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
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
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.xpath("./@src").extract_first())
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": img_url
               }
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
