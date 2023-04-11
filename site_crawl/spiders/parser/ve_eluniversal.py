# -*- coding: utf-8 -*-
# update:(liyun|2023-03-13) -> 发布日期修正
import re
from datetime import datetime
from urllib.parse import urljoin

import langdetect

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class EluniversalParser(BaseParser):
    name = 'eluniversal'
    
    # 站点id
    site_id = "7e5d3bef-15d7-4b9b-a024-6a7eca757649"
    # 站点名
    site_name = "委内瑞拉环球报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7e5d3bef-15d7-4b9b-a024-6a7eca757649", "source_name": "委内瑞拉环球报", "direction": "ve", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91235f7e-2f72-11ed-a768-d4619d029786", "国际", "https://www.eluniversal.com/buscador", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//a[span[@class="ellip"]]/@href').extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = response.xpath('//span[@id="autor"]/text()').extract()
        if authors:
            return [x.strip() for x in authors]
        return []

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//meta[@property="article:published_time"]/@content').extract_first(default="").strip()
            _date = re.search(r'(?P<d>\d+)\/(?P<m>\d+)\/(?P<y>\d+) (?P<H>\d+)\:(?P<M>\d+) (?P<T>\w+)', publish_date).groupdict()
            if _date["T"] == "pm":
                _date["H"] = int(_date["H"]) + 11
            publish_date = f'{_date["y"]}-{_date["m"]}-{_date["d"]} {_date["H"]}:{_date["M"]}:00'
            publish_date = datetime_helper.parseTimeWithOutTimeZone(
                datetime.strptime(publish_date, "%Y-%m-%d %H:%M:%S"),
                site_name="委内瑞拉环球报"
            )
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="note-text"]|//figure[@class="thumb img-bg"]/img|'
                                   '//div[@class="note-text"]/div/img|//div[@class="col-xs-12 col-md-9 notaest"]/*|'
                                   '//div[@class="col-xs-12 col-md-9 notaest"]//img')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "div", "p", "font"]:
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
