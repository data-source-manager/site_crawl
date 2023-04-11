# -*- coding: utf-8 -*-
import re
from datetime import timedelta, datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class TsjsParser(BaseParser):
    name = 'tsjs'
    
    # 站点id
    site_id = "f8daceef-d97b-488c-81ba-1ce14ae90dbd"
    # 站点名
    site_name = "当代日本研究学会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f8daceef-d97b-488c-81ba-1ce14ae90dbd", "source_name": "当代日本研究学会", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9123135c-2f72-11ed-a768-d4619d029786", "台日战略对话", "https://www.tsjs.org.tw/admin/news3/front/default/product_list.php?upid=2", "政治"),
            ("91231438-2f72-11ed-a768-d4619d029786", "国际研讨会", "https://www.tsjs.org.tw/admin/news3/front/default/product_list.php?upid=4", "政治"),
            ("912313d4-2f72-11ed-a768-d4619d029786", "青年论坛", "https://tsjs.org.tw/admin/news3/front/default/product_list.php?upid=1", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//li//a/@href').extract() or []
        if news_urls:
            for new in list(set(news_urls)):
                yield urljoin(response.url, new).replace("default/", "")

    def get_title(self, response) -> str:
        title = re.findall("<h1><p>(.*?)</p></h1>", response.text)
        if title:
            title = title[0]
        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        # 2022-07-18T11:27:12+03:00
        pub = response.xpath('//time/@data-datetime').extract_first()
        if pub:
            pub = pub.replace("T", " ").split("+")[0]
            pub_time = str(datetime.strptime(pub, "%Y-%m-%d %H:%M:%S") + timedelta(hours=+5))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        tags = response.xpath('//ul[@class="tag-list"]/li/a/text()').extract()
        if tags:
            return tags
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            '//div[@class="editor"]/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p"]:
                    img_list = news_tag.xpath(".//img/@src").extract()
                    if img_list:
                        for img in img_list:
                            img = urljoin(response.url, img)
                            dic = {"type": "image",
                                   "name": None,
                                   "md5src": self.get_md5_value(img) + '.jpg',
                                   "description": None,
                                   "src": img
                                   }
                            content.append(dic)
                    text_dict = self.parse_text(news_tag)
                    if text_dict.get("data"):
                        content.append(text_dict)
        image_list = response.xpath(
            '//div[@class="album_press"]/a/@href').extract()
        for img in image_list:
            img = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img) + '.jpg',
                   "description": None,
                   "src": img
                   }
            content.append(dic)
        return content

    def get_detected_lang(self, response) -> str:
        return "ko"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if "margin" in x.strip():
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
