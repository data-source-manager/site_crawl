# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from util.time_deal import translatetTime
from .base_parser import BaseParser


class Ru_scrfgovParser(BaseParser):
    name = 'ru_goverment'
    
    # 站点id
    site_id = "5feb0196-37ae-443e-ac0b-ab17476a11de"
    # 站点名
    site_name = "俄联邦安全会议"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "5feb0196-37ae-443e-ac0b-ab17476a11de", "source_name": "俄联邦安全会议", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91230fa6-2f72-11ed-a768-d4619d029786", "消息", "http://www.scrf.gov.ru/news/allnews/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@class='news']/a/@href").extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//article[@class='article']/h1/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        pass

    def get_pub_time(self, response) -> str:
        times_ = response.xpath('//article[@class="article"]/span[@class="info"]/text()').extract_first()
        day, month, year = re.findall("(\d{1,2}) (.*?) (\d{4}) года", times_)[0]
        time_ = year + "-" + translatetTime.ruDict[month] + "-" + day
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        pass

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='l-col1']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == 'div' and "read_media" in news_tag.root.get("class", ""):
                    img_dict = self.parse_img(response, news_tag, xpath_src=".//img/@src")
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
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
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, xpath_src='', xpath_des=''):
        if xpath_src:
            img_url = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(xpath_des).extract_first() if xpath_des else None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("//a[@class='entry_file_link']/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath("//h2[@class='aside_h2']/text()").extract_first(),
            "description": news_tag.xpath("//h3[@class='entry_title entry_title__file']/text()").extract_first(),
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
