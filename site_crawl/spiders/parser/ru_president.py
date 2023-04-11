# -*- coding: utf-8 -*-
from datetime import timedelta, datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class PresidentParser(BaseParser):
    name = 'president'
    
    # 站点id
    site_id = "34bfd4c1-448f-670d-f783-f27e56c3d2c4"
    # 站点名
    site_name = "白俄罗斯总统网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "34bfd4c1-448f-670d-f783-f27e56c3d2c4", "source_name": "白俄罗斯总统网", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块主题)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91231230-2f72-11ed-a768-d4619d029786", "事情发展", "https://president.gov.by/ru/events", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//li[@class="news-card"]//a[@class="news-card__title"]/@href').extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1/text()').extract_first(default="")
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
        image_list = response.xpath(
            '//section[contains(@class,"page-details__gallery")]/div[contains(@class,"gallery-thumbs")]//img/@src').extract()
        for img in image_list:
            img = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img) + '.jpg',
                   "description": response.xpath(".//p/text()").extract_first(),
                   "src": img
                   }
            content.append(dic)

        news_tags = response.xpath(
            '//section[@class="page-details__content"]/div/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict.get("data"):
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
