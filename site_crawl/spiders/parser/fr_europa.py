# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class FR_europaParser(BaseParser):
    name = 'europa'
    
    # 站点id
    site_id = "a28a9756-271c-4d2c-b77e-37d1bd47c450"
    # 站点名
    site_name = "欧盟边境管理局"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "a28a9756-271c-4d2c-b77e-37d1bd47c450", "source_name": "欧盟边境管理局", "direction": "fr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("912306dc-2f72-11ed-a768-d4619d029786", "多媒体", "https://frontex.europa.eu/media-centre/multimedia/videos/", "政治"),
            ("91230678-2f72-11ed-a768-d4619d029786", "新闻稿", "https://frontex.europa.eu/media-centre/news/news-release/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//article/h3/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = 'https://frontex.europa.eu/' + news_url
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='col-md-8 col-md-offset-2']/h2/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        pass

    def get_pub_time(self, response) -> str:
        time_ = response.xpath("//span[@class='date']/text()").extract_first() or ""
        dt = datetime_helper.fuzzy_parse_timestamp(time_)
        if dt:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@class='text-content']/*|//div[@class='col-md-8 col-md-offset-2']/figure|//div[@class='col-md-8 col-md-offset-2']//iframe")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "figure":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag == 'iframe':
                    video_dict = self.parse_media(response, news_tag)
                    content.append(video_dict)
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
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.xpath("./img/@src").extract_first())
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": img_url}
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
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
