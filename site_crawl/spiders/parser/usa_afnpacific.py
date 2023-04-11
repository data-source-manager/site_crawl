# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Usa_afnpacificParser(BaseParser):
    name = 'usa_afnpacific'
    
    # 站点id
    site_id = "1ff8b89c-8d51-4eeb-9a5b-e844da7ea494"
    # 站点名
    site_name = "太平洋美军网络"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "1ff8b89c-8d51-4eeb-9a5b-e844da7ea494", "source_name": "太平洋美军网络", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91232054-2f72-11ed-a768-d4619d029786", "最新视频", "https://www.afnpacific.net/Video/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@class='DVIDSCarouselItem']/a/@href").extract() or ""
        if news_urls:
            for news_url in news_urls:
                re_patterns = re.findall("GetCCURL\(\'(.*?)\'\)", news_url)[0]
                if not re_patterns.startswith('http'):
                    re_patterns = urljoin(response.url, re_patterns)
                yield re_patterns

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='DVIDSMediaTitle']/text()").extract_first() or ""
        return title

    def get_author(self, response) -> list:
        author = []
        author_a = response.xpath("//span[@class='mediaCredits']/text()").extract_first()
        if author_a:
            author.append(author_a.replace("Video by", "").strip())
        return author

    def get_pub_time(self, response) -> str:
        time_str = response.xpath("//div[@class='DVIDSMediaDate']/text()").extract_first() or ""
        dt = time_str.replace("|", "")
        dt_ = datetime_helper.fuzzy_parse_timestamp(dt)
        if dt_:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath("//div[@class='DVIDSMediaTags']/span/a/text()").extract()
        tags = [tags.strip() for tags in tags_node]
        return tags

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='DVIDSMediaDescription']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p", "span"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
        media_src = response.xpath("//button[@id='playerDownload']/a/@href").extract_first()
        if media_src:
            video_type = media_src.split(".")[-1]
            video_dic = {
                "type": "video",
                "src": media_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(media_src) + "." + video_type
            }
            content.append(video_dic)
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

    def parse_img(self, response, news_tag, xpath_src='', xpath_des=''):
        pass

    def parse_file(self, response):
        file_src = response.url
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag, xpath_src='', xpath_des=''):
        video_src = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": news_tag.xpath(xpath_des).extract_first(),
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
