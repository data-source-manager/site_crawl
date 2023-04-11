# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import langdetect

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class JacksonvilleParser(BaseParser):
    name = 'jacksonville'
    
    # 站点id
    site_id = "eb738124-946b-4270-8f85-ae99595122a1"
    # 站点名
    site_name = "杰克逊维尔海军医院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "eb738124-946b-4270-8f85-ae99595122a1", "source_name": "杰克逊维尔海军医院", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91233a4e-2f72-11ed-a768-d4619d029786", "文章", "https://jacksonville.tricare.mil/News-Gallery/Articles/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        urls = response.xpath('//p[@class="title"]/a/@href').extract()
        if urls:
            for url in urls:
                yield urljoin(response.url, url)
                # yield "https://jacksonville.tricare.mil/News-Gallery/Articles/Article/3028304/patients-at-naval-branch-health-clinic-kings-bay-can-take-steps-now-to-prepare/"

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="title"]/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        author = response.xpath('//p[@class="info"]/span[1]/text()').extract_first()
        if author:
            author = author.replace("By", "").strip()
            return [author]
        return []

    def get_pub_time(self, response) -> str:
        # 2022-01-21T03:21:00.2100000
        pub = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
            pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        tag_list = []
        tags = response.xpath('//div[@class="tags"]//a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tag_list.append(tag.strip())
        return tag_list

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="image"]/img')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))
        img_list_length = len(img_list)
        news_tags = response.xpath(
            '//div[@itemprop="articleBody"]/span|'
            '//div[@itemprop="articleBody"]/ul/li|'
            '//div[@itemprop="articleBody"]/text()'
        )
        if news_tags:
            for news_tag in news_tags:
                if type(news_tag.root) == str:
                    dic = {}
                    if news_tag.root.strip():
                        dic["data"] = news_tag.root.strip()
                        dic["type"] = "text"
                        content.append(dic)
                else:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "li"]:
                        text_dict = self.parse_text(news_tag)
                        content.extend(text_dict)
        news_content = []
        for i, con in enumerate(content):
            if i == img_list_length:
                continue
            if i == img_list_length + 1:
                con["data"] = content[i - 1].get("data") + con.get("data")
            news_content.append(con)
        return news_content

    def get_detected_lang(self, response) -> str:
        title = self.get_title(response)
        if title:
            return langdetect.detect(f"{title}")
        else:
            print('error, no title url:' + response.url)
            return ''

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('alt'),
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
