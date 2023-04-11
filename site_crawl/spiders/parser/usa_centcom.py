# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class UsaCentcomParser(BaseParser):
    name = 'centcom'
    
    # 站点id
    site_id = "2dd4ad08-87c5-4461-9923-0ae0f9d42e37"
    # 站点名
    site_name = "美国中央司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "2dd4ad08-87c5-4461-9923-0ae0f9d42e37", "source_name": "美国中央司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("72c6b646-f7f7-39f7-852b-81c8e1f4057d", "媒体", "https://www.centcom.mil/MEDIA/", "政治"),
            ("4a8e22bc-fe6f-11ec-a30b-d4619d029786", "媒体/新闻文章", "https://www.centcom.mil/MEDIA/NEWS-ARTICLES/", "政治"),
            ("4a8e2352-fe6f-11ec-a30b-d4619d029786", "媒体/新闻稿", "https://www.centcom.mil/MEDIA/PRESS-RELEASES/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = '2dd4ad08-87c5-4461-9923-0ae0f9d42e37'

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="alist news "]/div//p/a/@href|'
                                   '//div[@class="title"]/a/@href|'
                                   '//div[@class="DGOVImageGallerylvImage"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="title"]/text()|//div[@id="spanTitle"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//p[@class="info"]/span[@class="line"]/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.replace("By", "").strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="image"]/img|//a[@id="aImgImage"]/img')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))

        img_list_length = len(img_list)

        news_tags = response.xpath('//div[@class="body"]/*|//div[@id="spanCaption"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
        drop_con = content[img_list_length]
        new_content = []
        for x in range(len(content)):
            if x == img_list_length:
                continue
            if x == img_list_length + 1:
                content[x]["data"] = drop_con["data"] + content[x]["data"]
            new_content.append(content[x])
        return new_content

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

    def parseOneText(self, news_tag) -> list:
        """"
            一个标签下只有一段但是存在其他标签
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            if "".join(cons).strip():
                dic['data'] = "".join(cons).strip()
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
                   "src": img_url}
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
