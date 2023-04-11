# -*- coding: utf-8 -*-
# update: [liyun:2023-01-16] -> 板块核对与修正

import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaUsipParser(BaseParser):
    name = 'usip'
    # 站点id
    site_id = "ac99eb18-7649-46c2-8dbd-97d867d9679a"
    # 站点名
    site_name = "美国和平研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "ac99eb18-7649-46c2-8dbd-97d867d9679a", "source_name": "美国和平研究所", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("03e8850d-6ea4-ba41-0262-5828ea5012b6", "地区", "", "政治"),
            ("e1148d43-5b40-4a1b-9cef-c0a1d923ef1d", "地区/中国", "https://www.usip.org/regions/asia/china", "政治"),
            ("59e8ed70-579d-434e-b922-c2e5a53e1840", "地区/俄罗斯", "https://www.usip.org/regions/europe/russia", "政治"),
            ("afefe6d9-3dbc-3ada-b2e2-999f8b078b35", "问题领域", "", "政治"),
            ("4a8b54a6-fe6f-11ec-a30b-d4619d029786", "问题领域/全球政策", "https://www.usip.org/issue-areas/global-policy", "政治"),
            ("e4620a06-3a2f-4a22-9a08-6c10254ad555", "问题领域/经济", "https://www.usip.org/issue-areas/economics", "经济"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "ac99eb18-7649-46c2-8dbd-97d867d9679a"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h3[@class="summary__heading"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//article/header/p[@class="meta"]/a/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//article/header/p[@class="meta"]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_.strip())
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        for tag in response.xpath(
                '//main/section/article/section/*'
                '|//main/section/article//img'
        ):
            if tag.root.tag in ["p", "h2", "h3", "h4"]:
                text = " ".join(tag.xpath('.//text()').extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag == "img":
                img_url = urljoin(response.url, tag.attrib.get("src", "").split("?")[0])
                suffix = img_url.split(".")[-1].lower()
                if suffix not in ["jpg", "png", "jpeg"]:
                    continue
                content.append({
                    "type": "image",
                    "name": None,
                    "md5src": self.get_md5_value(img_url) + f'.{suffix}',
                    "description": tag.attrib.get("alt", "").strip(),
                    "src": img_url
                })
            else:
                pass
        return content

        # news_tags = response.xpath('//main/article/section/p|'
        #                            '//main/article/section/figure|'
        #                            '//main/section/article/section/p|'
        #                            '//main/section/p')
        # if news_tags:
        #     for news_tag in news_tags:
        #         if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
        #             text_dict = self.parse_text(news_tag)
        #             if text_dict:
        #                 content.extend(text_dict)
        #         if news_tag.root.tag == "figure":
        #             con_img = self.parse_img(response, news_tag)
        #             if con_img:
        #                 content.append(con_img)

        # return content

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
                   "description": "".join(news_tag.xpath('.//figcaption/text()').extract()).strip(),
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
