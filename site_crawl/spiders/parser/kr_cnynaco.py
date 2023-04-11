# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_cnynacoParser(BaseParser):
    name = 'kr_cnynaco'
    
    # 站点id
    site_id = "e24f02f6-ce7a-4946-b567-7962fbbf5cc9"
    # 站点名
    site_name = "韩联社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e24f02f6-ce7a-4946-b567-7962fbbf5cc9", "source_name": "韩联社", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("38946f59-38ae-4527-b228-11ff7bc3b972", "政治", "https://cn.yna.co.kr/politics/index", "政治"),
            ("c3bd6681-d93d-4283-a52c-f8477f2c88c9", "朝鲜", "https://cn.yna.co.kr/nk/index", "政治"),
            ("58691776-7327-4125-827b-4b5d11f85a2b", "视频", "https://cn.yna.co.kr/video/index", "政治"),
            ("c951ae81-b22a-471f-a097-ec7966516236", "韩中关系", "https://cn.yna.co.kr/china-relationship/index", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//h2[@class='tit']/a/@href|//h1[@class='tit']/a/@href|//article//h4[@class='tit']/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='tit']/text()|//h1[@class='tit02']/text()").get()
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//meta[@property='article:published_time']/@content").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@class='tag']/span/a/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        if "ACK20221115001000881" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url)
            }
            content.append(file_dic)
        else:
            news_tags = response.xpath(
                "//div[@class='inner']/*|//div[contains(@class,'yna-img-slide') or contains(@class,'img-thumb')]//img|"
                "//div[@class='txt-desc']/*|//video[@id='todayVideoPlay']")
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p"]:
                        text_dict = self.parse_text(news_tag)
                        if text_dict:
                            content.append(text_dict)
                    elif news_tag.root.tag == "img":
                        con_img = self.parse_img(response, news_tag, img_xpath="./@src", des_xpath="./@alt")
                        if con_img:
                            content.append(con_img)
                    elif news_tag.root.tag == "video":
                        video_src = self.parse_media(response, news_tag)
                        if video_src:
                            content.append(video_src)

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
