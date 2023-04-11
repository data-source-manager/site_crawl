# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class BrookingsParser(BaseParser):
    name = 'brookings'
    
    # 站点id
    site_id = "604388a5-6ef0-4cee-9a4f-404f869ba688"
    # 站点名
    site_name = "布鲁金斯学会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "604388a5-6ef0-4cee-9a4f-404f869ba688", "source_name": "布鲁金斯学会", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("3285ee5b-12e3-4f79-bc96-f8c07251d348", "全球发展", "https://www.brookings.edu/topic/global-development/", "政治"),
            ("0ba6ccee-d28c-3a1c-8c21-2b8be5e3c812", "国防与安全", "https://www.brookings.edu/topic/defense-security/", "政治"),
            ("4a8bccf6-fe6f-11ec-a30b-d4619d029786", "国际事务", "https://www.brookings.edu/topic/international-affairs/?type=posts", "政治"),
            ("4a8bcd64-fe6f-11ec-a30b-d4619d029786", "美国外交政策博客文章", "https://www.brookings.edu/topic/u-s-foreign-policy/?type=posts", "政治"),
            ("25d4de21-9848-46d9-929d-bb604739a1b6", "美国政治与政府", "https://www.brookings.edu/topic/u-s-politics-government/", "政治"),
            ("c19d9ad7-2f52-4b7b-aa97-81167f2129ca", "美国经济", "https://www.brookings.edu/topic/u-s-economy/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "604388a5-6ef0-4cee-9a4f-404f869ba688"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="list-content"]/article//h4/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//meta[@property="og:image"]/@content').extract_first()
        if img_list:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_list) + '.jpg',
                   "description": None,
                   "src": img_list
                   }
            content.append(dic)

        news_tags = response.xpath(
            '//div[@itemprop="articleBody"]/p|//div[@class="new-essay__wrapper post-body"]/div[@class="core-block"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "a"]:
                    text_dict = self.parseOnetext(news_tag)
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
            oneCons = "".join(cons).strip().replace('\xa0', '').replace('\t', '').replace('\n', '').replace('\r', '')
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
