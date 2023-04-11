# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class TexasParser(BaseParser):
    name = 'texas'
    
    # 站点id
    site_id = "b1ad10af-c06c-447c-8391-3adff3d92ad2"
    # 站点名
    site_name = "美国德州军事部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "b1ad10af-c06c-447c-8391-3adff3d92ad2", "source_name": "美国德州军事部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91231dde-2f72-11ed-a768-d4619d029786", "新闻", "https://tmd.texas.gov/news", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.urltimedict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h1[@class="blogtitle"]/a/@href').extract() or []
        if news_urls:
            for news in news_urls:
                url = urljoin(response.url, news)
                yield url

    def get_title(self, response) -> str:
        title = response.xpath('//h2/text()').extract_first(default="") or ""

        return title.strip() or ""

    def get_author(self, response) -> list:
        author = response.xpath('//span[@class="blogauthor"]//text()').extract_first()
        if author.strip():
            return [author.split("by")[1].strip()]
        else:
            return []

    def get_pub_time(self, response) -> str:
        # Wednesday, January 5, 2022 9:37:00
        new_time = response.xpath('//span[@class="bdate"]/text()').extract_first()
        if new_time:
            pub = new_time.replace("AM", "").replace("PM", "").strip().split(",")[1:]
            return str(datetime.strptime("".join(pub).strip(), "%B %d %Y %H:%M:%S"))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags = response.xpath('//span[@class="blogtags"]/a/text()').extract()
        if tags:
            return tags
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('///div[@class="blogtext"]/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p", "li"]:
                    img = news_tag.xpath("./img/@src").extract_first()
                    if img:
                        img_dict = self.parse_img(response, news_tag)
                        if img_dict.get("data"):
                            content.append(img_dict)
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
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.xpath("./img/@src").extract_first())
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
