# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class UsaPacomParser(BaseParser):
    name = 'pacom'
    
    # 站点id
    site_id = "63f3e7a4-8e0a-453e-80d9-07ed9c7b5cfc"
    # 站点名
    site_name = "美国印太司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "63f3e7a4-8e0a-453e-80d9-07ed9c7b5cfc", "source_name": "美国印太司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8becf4-fe6f-11ec-a30b-d4619d029786", "新闻", "https://www.pacom.mil/Media/News/", "政治"),
            ("a0bcc776-b731-3b1c-841d-e6e7008d0220", "演讲", "", "政治"),
            ("4a8bf1a4-fe6f-11ec-a30b-d4619d029786", "演讲/证词", "https://www.pacom.mil/Media/Speeches-Testimony/", "政治"),
            ("4a8bf352-fe6f-11ec-a30b-d4619d029786", "相片", "https://www.pacom.mil/Media/Photos/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//span[@class="title"]/a/@href|'
                                   '//div[@class="ImageGallerylvImage"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "Photos" in response.url:
            return "美国印太司令部_photo"
        title = response.xpath('//meta[@name="twitter:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@class="tags"]/div//a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="image"]/img|'
                                  '//div[@class="ImageImg"]//img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//div[@itemprop="articleBody"]/p|'
                                   '//span[@id="spanCaption"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
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
        img = news_tag.xpath('.//@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//@alt').extract()).strip(),
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
