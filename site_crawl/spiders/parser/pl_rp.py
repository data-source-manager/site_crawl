# -*- coding: utf-8 -*-
import re
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class PlRparser(BaseParser):
    name = 'rp'
    # 站点id
    site_id = "ac40e9c7-3ba0-41ad-8ee4-f3d4383fc526"
    # 站点名
    site_name = "共和国报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "ac40e9c7-3ba0-41ad-8ee4-f3d4383fc526", "source_name": "共和国报", "direction": "pl", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("55f506f4-c27a-4a0b-bef0-1863dc1558f6", "事件", "", "政治"),
            ("e920c320-9408-45b4-b4c9-e99e867dc1a1", "事件/世界", "https://www.rp.pl/wydarzenia/swiat", "政治"),
            ("ca86bcad-8859-48ef-a35d-caaaab7cfc4b", "事件/国家", "https://www.rp.pl/wydarzenia/kraj", "政治"),
            ("4e477f37-a3e3-4f2b-8736-cc6208c7827e", "地区", "", "政治"),
            ("cf0c3584-2ce5-4174-84a1-2bd0852bfa25", "地区/讨论", "https://regiony.rp.pl/regiony/dyskusje", "政治"),
            ("fa9c228a-aa8b-4701-8fd0-78002892f8d0", "新闻学", "", "政治"),
            ("4ae8be16-3d75-4264-b3e4-14e5b8e5101b", "新闻学/政治和社会观点", "https://www.rp.pl/publicystyka/opinie-polityczno-spoleczne", "政治"),
            ("519e446c-c171-4450-9fca-bafbc524d4fb", "新闻学/评论", "https://www.rp.pl/publicystyka/komentarze", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="col--fill"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="twitter:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//div[@class="author"]/p//text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        06.03.2023 03:00
        """
        # %d.%m.%Y %H:%M
        time_ = re.findall('datePublished":"(.*?)"', response.text)
        if time_:
            return datetime_helper.parseTimeWithTimeZone(time_[0])

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//a[@class="tag--comp"]/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="blog--image"]')
        if img_list:
            con_img = self.parse_img(response, img_list)
            if con_img:
                content.append(con_img)

        news_tags = response.xpath('//div[@id="articleBody"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "p", ]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

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
            oneCons = "".join(cons).strip()
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
                   "description": news_tag.xpath('./p/text()').extract_first().strip(),
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
        videoUrl = news_tag.xpath("").extract_first()
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
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
