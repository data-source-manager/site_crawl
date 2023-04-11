# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class ID_thejakartapost(BaseParser):
    name = 'id_thejakartapost'
    
    # 站点id
    site_id = "06ec3006-bd05-4a92-b539-b6ce82451c42"
    # 站点名
    site_name = "雅加达邮报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "06ec3006-bd05-4a92-b539-b6ce82451c42", "source_name": "雅加达邮报", "direction": "id", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("127f9712-f57e-3255-8553-c0bad814eef3", "世界", "", "政治"),
            ("4a8d7876-fe6f-11ec-a30b-d4619d029786", "世界/中东和非洲", "https://www.thejakartapost.com/world/middle-east-africa", "政治"),
            ("4a8d7646-fe6f-11ec-a30b-d4619d029786", "世界/亚太地区", "https://www.thejakartapost.com/world/asia-pacific", "政治"),
            ("4a8d77d6-fe6f-11ec-a30b-d4619d029786", "世界/欧洲", "https://www.thejakartapost.com/world/europe", "政治"),
            ("4a8d76fa-fe6f-11ec-a30b-d4619d029786", "世界/美洲", "https://www.thejakartapost.com/world/americas", "政治"),
            ("1fd86184-92be-3266-9f00-5f06e1478288", "观点", "", "政治"),
            ("4a8d74de-fe6f-11ec-a30b-d4619d029786", "观点/分析", "https://www.thejakartapost.com/academia/analysis", "政治"),
            ("4a8d75a6-fe6f-11ec-a30b-d4619d029786", "观点/洞察力", "https://www.thejakartapost.com/academia/insight", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//div[contains(@class,'bigHeadline') or contains(@class,'smallHeadline')]/div[@class='listNews']/div[@class='descNews']/a[2]/@href|//div[@class='columnsNews d-flex']//div[@class='latestDetail']/a[2]/@href").extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='title-large']/text()").get()
        return title or ""

    def get_author(self, response) -> list:
        authors = []
        auhtor_str = response.xpath("//span[@class='date'][1]/a/strong/text()").get()
        if auhtor_str:
            authors.append(auhtor_str)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//span[@class='day']/text()").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@class='topicRelated mt-20']/ul/li/a/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[contains(@class,'detailNews')]/*|//div[@class='row']/img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src",
                                             des_xpath="//span[@class='created']/text()")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
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
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
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
        video_src = news_tag.xpath("./source/@src").extract_first()
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(video_src) + ".mp4"
        }
        return video_dic

    def get_like_count(self, response) -> int:
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
