# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class KrSejongEnParser(BaseParser):
    name = 'sejong'
    
    # 站点id
    site_id = "782605b6-29be-435c-9f32-d388634aea0f"
    # 站点名
    site_name = "世宗研究所英文网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "782605b6-29be-435c-9f32-d388634aea0f", "source_name": "世宗研究所英文网", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("76efe287-5621-4d98-88a4-33e13959eed3", "世宗政策研究", "https://sejong.org/web/boad/22/egolist.php?bd=34", "政治"),
            ("a00f518b-f361-4cb3-85ef-e54c5e85eb8b", "世宗解说", "https://sejong.org/web/boad/22/egolist.php?bd=22", "政治"),
            ("ccacb91b-772a-4e35-e6bb-19443668e375", "刊物", "", "政治"),
            ("fb6f80d2-71a2-4bd1-99ef-09ea50f82042", "刊物/世宗政策简报", "https://sejong.org/web/boad/1/egolist.php?bd=3", "政治"),
            ("0a6b4178-ec45-4303-8ff3-d5e9a5bfc88c", "刊物/国家战略", "https://sejong.org/web/boad/1/egolist.php?bd=3", "政治"),
            ("a95d6ed7-b471-4080-9360-b2bcbe09516b", "国家战略", "https://sejong.org/web/boad/22/egolist.php?bd=36", "政治"),
            ("837e173b-c62e-41d4-9a73-8f51f42b2a27", "形势与政策", "https://sejong.org/web/boad/22/egolist.php?bd=23", "政治"),
            ("d5c5003c-9b80-4013-a0e4-3ced4ab8e1b4", "研究报告", "https://sejong.org/web/boad/22/egolist.php?bd=57", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "782605b6-29be-435c-9f32-d388634aea0f"
    def parse_list(self, response) -> list:
        news_urls = response.xpath('//p[@class="lt_tit pb15"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="title"]/@content').extract_first(default="")
        if ")" in title and title.strip().startswith("("):
            title = title.split(")")[1]
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//div[@class="view_w"]//span[contains(@class,"date")]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_.strip())
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="view_bx04"]/div/*|//div[@class="view_bx02"]//a|'
                                   '//div[@class="post_text pb60"]/p/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)

        return content

    def get_detected_lang(self, response) -> str:
        return "en"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip().replace('\xa0', '').replace('\n', '').replace('\r', '').replace('\u200b',
                                                                                                            '')
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//figcaption//text()').extract()).strip(),
                   "src": img_url
                   }
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath(".//@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.attrib.get('title'),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("./@href").extract_first()
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": news_tag.xpath('./span/text()').extract_first().strip(),
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
        read = response.xpath('//div[@class="view_w"]//span[contains(@class,"hit")]/text()').extract_first()
        return read.strip() if read else 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
