# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import langdetect

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class OhmynewsParser(BaseParser):
    name = 'ohmynews'
    
    # 站点id
    site_id = "415c28a7-8a20-4bc2-9a8c-f12bf7df0995"
    # 站点名
    site_name = "OhMyNews"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "415c28a7-8a20-4bc2-9a8c-f12bf7df0995", "source_name": "OhMyNews", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91234a20-2f72-11ed-a768-d4619d029786", "国家和国际", "http://www.ohmynews.com/NWS_Web/ArticlePage/Total_Article.aspx?PAGE_CD=C0600", "政治"),
            ("912349bc-2f72-11ed-a768-d4619d029786", "政治", "http://www.ohmynews.com/NWS_Web/ArticlePage/Total_Article.aspx?PAGE_CD=C0400", "政治"),
            ("912349ee-2f72-11ed-a768-d4619d029786", "经济", "http://www.ohmynews.com/NWS_Web/ArticlePage/Total_Article.aspx?PAGE_CD=C0300", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="news_list"]/div/dl/dt/a/@href').extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                news_url = urljoin(response.url, news_url)
                yield news_url
                # 报错原因可能是中继失败

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = response.xpath('//div[@class="info_data"]/div/a/text()').extract()
        if authors:
            return [x.strip() for x in authors]
        return []

    def get_pub_time(self, response) -> str:
        # 16.07.2022 – 23:42
        pub = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        tags = response.xpath('//meta[@name="news_keywords"]/@content').extract_first()
        if tags:
            tags = tags.split(',')
            return [x.strip() for x in tags]
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="at_contents"]|//article[@itemprop="articleBody"]'
                                   '//article[@class="article_body at_contents article_view"]|'
                                   '//article[@class="article_body at_contents article_view"]//img|'
                                   '//div[@class="at_contents"]/table//img|//div[@class="view-txt"]|'
                                   '//div[@class="special_photo_box"]/img')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "div", "p", "article"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict.get("data"):
                        content.append(text_dict)
                if news_tag.root.tag == 'img':
                    img_dict = self.parse_img(response, news_tag)
                    if img_dict:
                        content.append(img_dict)
        return content

    def get_detected_lang(self, response) -> str:
        title = self.get_title(response)
        if title:
            return langdetect.detect(f"{title}")
        else:
            print('error, no title url:' + response.url)
            return ''

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('./text()').extract() or ""
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
        try:
            count = response.xpath('//a[@id="top_recm"]/text()').extract_first()
            like_count = int(count)
            return like_count
        except:
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
