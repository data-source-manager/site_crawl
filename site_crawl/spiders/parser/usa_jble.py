# -*- coding: utf-8 -*-
import time
from datetime import datetime
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class JbleParser(BaseParser):
    name = 'jble'
    
    # 站点id
    site_id = "a126ef80-8cfa-4cd5-9e84-43abc950ee65"
    # 站点名
    site_name = "兰利空军基地"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "a126ef80-8cfa-4cd5-9e84-43abc950ee65", "source_name": "兰利空军基地", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("912328d8-2f72-11ed-a768-d4619d029786", "消息", "https://www.jble.af.mil/News/Features/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.pdfdict = {}

    def parse_list(self, response) -> list:
        url_list = response.xpath('//p[@class="title"]/a/@href').extract()
        if url_list:
            for x in url_list:
                yield urljoin(response.url, x)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="title"]/text()').extract_first(default="") or ""
        if title:
            return title.strip()

    def get_author(self, response) -> list:
        author = response.xpath('//p[@class="info"]/span[1]/text()').extract_first()
        if author:
            return author.replace("By", "").strip()
        return []

    def get_pub_time(self, response) -> str:
        # July 18, 2017
        # Nov. 28, 2018
        new_time = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if new_time:
            if "." in new_time:
                pub_time = datetime_helper.fuzzy_parse_timestamp(new_time)
                pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
                return pub_time
            else:
                return str(datetime.strptime(new_time.strip(), "%B %d, %Y"))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags = []
        tag = response.xpath('//div[@class="tags"]/a/text()').extract()
        if tag:
            for x in tag:
                if x.strip():
                    tags.append(x)
        return tags

    def get_content_media(self, response) -> list:
        content = []
        img_url = urljoin(response.url, response.xpath('//div[@class="image"]/img/@src').extract_first())
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": response.xpath("//div[@class='image']/img/@alt").extract_first(),
               "src": img_url
               }
        content.append(dic)

        news_tags = response.xpath(
            '//div[@class="body"]/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p", "div"]:
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
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.xpath(".//img/@src").extract_first())
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": "".join(news_tag.xpath('.//div[@class="altCap"]/p//text()').extract()),
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
