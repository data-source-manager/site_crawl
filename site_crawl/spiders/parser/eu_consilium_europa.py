# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Euconsilium_europaParser(BaseParser):
    name = 'consilium_europa'
    
    # 站点id
    site_id = "dca0cae2-645d-428e-9951-9854f18e2301"
    # 站点名
    site_name = "欧洲理事会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "dca0cae2-645d-428e-9951-9854f18e2301", "source_name": "欧洲理事会", "direction": "fr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91230c7c-2f72-11ed-a768-d4619d029786", "新闻稿", "https://www.consilium.europa.eu/en/press/press-releases/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@class='inline-items']/h3[@class='h5']/a/@href").extract() or ""
        titles = response.xpath("//div[@class='inline-items']/h3[@class='h5']/a/text()").extract() or ""
        if news_urls:
            for index, news_url in enumerate(news_urls):
                if not news_url.startswith('http'):
                    news_url = 'https://www.consilium.europa.eu/' + news_url
                self.Dict[news_url] = titles[index]
                yield news_url

    def get_title(self, response) -> str:
        return self.Dict[response.url]

    def get_author(self, response) -> list:
        pass

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.xpath(
            "//ul[@class='d-inline-block vertical-divider list-inline small']/li[position()>2]/text()").extract() or ""
        dt = time_[0]
        if len(time_) > 1:
            dt = time_[0] + " " + time_[1]
            dt_ = datetime_helper.fuzzy_parse_timestamp(dt)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        elif len(time_) == 1:
            dt_ = datetime_helper.fuzzy_parse_timestamp(dt)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath("//a[@class='btn btn-topic']/text()").extract()
        return [tags.strip() for tags in tags_node]

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[contains(@class,'council-left-content-basic council-flexify')]/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        if li.xpath("./a[contains(@href,'pdf')]/@href"):
                            file_dict = self.parse_file(response, li)
                            content.append(file_dict)
                        text_dict = self.parse_text(li)
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

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("./a[contains(@href,'pdf')]/@href").extract_first())
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
