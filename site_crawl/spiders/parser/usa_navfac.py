# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class NavfacParser(BaseParser):
    name = 'navfac'
    
    # 站点id
    site_id = "a3dfa5a7-1694-4d37-a13b-fcff395e7d13"
    # 站点名
    site_name = "海军设施工程系统司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "a3dfa5a7-1694-4d37-a13b-fcff395e7d13", "source_name": "海军设施工程系统司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91232ab8-2f72-11ed-a768-d4619d029786", "媒体", "https://www.navfac.navy.mil/Media/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.DICT1 = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="a-summary"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1/text()").extract_first()
        if title:
            return title.strip()
        return ""

    def get_author(self, response) -> list:
        pass

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//div[@class="press-briefing__date"]/text()').extract_first() or ""
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
            return pub_time
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('//div[@class="acontent-container"]/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "p":
                    content.extend(self.parse_text(news_tag))

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

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

    def parse_img(self, response, news_tag, descrption_xpath):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": response.xpath(descrption_xpath).extract_first(),
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag, description_xpath):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": news_tag.xpath(description_xpath).extract_first(),
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
