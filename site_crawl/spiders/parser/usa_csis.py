# -*- coding: utf-8 -*-
import re
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal.datetime_helper import parseTimeWithOutTimeZone, parseTimeWithTimeZone

"""
    模版
"""


class UsaCsisParser(BaseParser):
    name = 'csis'
    
    # 站点id
    site_id = "3a005e07-1c2b-4727-a68a-16b42739190a"
    # 站点名
    site_name = "战略与国际研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "3a005e07-1c2b-4727-a68a-16b42739190a", "source_name": "战略与国际研究中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("7629929d-3bf4-4716-968e-48e20ed340df", "事件", "https://www.csis.org/events?f%5B0%5D=event_type%3A3004&f%5B1%5D=event_type%3A3005&f%5B2%5D=event_type%3A3012", "政治"),
            ("4a8b4cb8-fe6f-11ec-a30b-d4619d029786", "北约", "https://www.csis.org/search?f%5B0%5D=field_categories%253Afield_regions%3A805", "政治"),
            ("98c0cbdc-abe2-8b91-31b0-49da11b2cd92", "按地区", "", "政治"),
            ("d821b0a0-eb4b-445f-a721-2a534ac42eae", "按地区/中东", "https://www.csis.org/analysis?f%5B0%5D=regions%3A785", "政治"),
            ("653fa447-1a6b-4ccb-8f4b-b45420bcd62a", "按地区/亚洲", "https://www.csis.org/regions/asia?f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport", "政治"),
            ("600188de-fcb9-40bc-8cf1-a4786f977c63", "按地区/俄罗斯和欧亚大陆", "https://www.csis.org/analysis?f%5B0%5D=regions%3A802", "政治"),
            ("f3c6a913-968f-4ee2-a3a7-5ff3b777344d", "按地区/北极", "https://www.csis.org/regions/arctic?f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport", "政治"),
            ("060fbe21-7156-45a6-aa4e-76b0d84a2b16", "按地区/欧洲", "https://www.csis.org/analysis?f%5B0%5D=regions%3A787", "政治"),
            ("0d92a1e2-3001-43c7-ba5a-1b97ec806a62", "按地区/美洲", "https://www.csis.org/regions/americas?f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport", "政治"),
            ("ca06d127-7504-4520-a90f-38a0f82950dc", "按地区/非洲", "http://csis.org/analysis?f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport&f%5B2%5D=regions%3A789", "政治"),
            ("eaead364-172c-b0ca-951d-3802a44d8e04", "按类型", "", "政治"),
            ("9b4226dd-2c41-4b74-bdd6-d5c216348444", "按类型/国防与安全", "https://www.csis.org/search?f%5B0%5D=field_categories%253Afield_topics%3A817&page=1", "政治"),
            ("364efea2-b7b2-4763-8351-ae22be87c179", "按类型/国际发展", "https://www.csis.org/topics/international-development?f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport", "政治"),
            ("f35b0066-c848-443d-b877-9be40d810d14", "按类型/经济", "https://www.csis.org/topics/economics?f%5B0%5D=content_type%3Aarticle&f%5B1%5D=content_type%3Areport", "政治"),
            ("4a8b4c72-fe6f-11ec-a30b-d4619d029786", "美国发展政策", "https://www.csis.org/search?f%5B0%5D=field_categories%253Afield_topics%3A833", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "3a005e07-1c2b-4727-a68a-16b42739190a"
        self.time = {}
        self.author = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@class="hocus-headline"]/@href').extract()
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="citation_title"]/@content|'
                               '//h1[contains(@class,"headline")]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="citation_author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
           Mar 3, 2023
        """
        time_re = re.findall('date_published":"(.*?)"', response.text)
        time_ = time_re if "".join(time_re).strip() else response.xpath('//div[contains(@class,"event-status tag")]/@data-start-date').extract()
        if "".join(time_).strip():
            if "T" in "".join(time_).strip():
                return parseTimeWithTimeZone(time_[0])
            else:
                time_ = datetime.strptime(time_[0], "%b %d, %Y")
            return parseTimeWithOutTimeZone(time_, site_name="战略与国际研究中心")

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="text-block ts-friendly"]//p|'
                                   '//div[@class="hero--field-featured-image image--full"]//img|'
                                   '//div[@class="md:relative md:z-2"]/ul/li/a')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)
                if news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

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
        img = news_tag.xpath('./@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.attrib.get('alt'),
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
