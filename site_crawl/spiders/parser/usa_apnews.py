# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class UsaApnewsParser(BaseParser):
    name = 'apnews'
    
    # 站点id
    site_id = "8f198a52-cf4d-4fae-8394-4223c826c82a"
    # 站点名
    site_name = "联合通讯社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "8f198a52-cf4d-4fae-8394-4223c826c82a", "source_name": "联合通讯社", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b459c-fe6f-11ec-a30b-d4619d029786", "政治", "https://apnews.com/hub/politics?utm_source=apnewsnav&utm_medium=navigation", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@data-key="card-headline"]/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="twitter:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//span[contains(@class,"Component-bylines")]/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    au = au.replace("By", "").strip()
                    if "and" in au:
                        au = au.split("and")
                        return au
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[contains(@class,"Timestamp")]/@data-source').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        first_img = response.xpath('//meta[@property="twitter:image"]/@content').extract_first()
        if first_img:
            flag_id = re.findall('https://storage.googleapis.com/afs-prod/media/(.*?)/\d+.jpeg', first_img)
            if flag_id:
                flag_id = flag_id[0]
                img_id_list = re.findall('"mediumIds":(\[\S+\])', response.text)
                if img_id_list:
                    for img_id in img_id_list:
                        img_id = img_id.replace("[", "").replace("]", "").replace('"', "")
                        if img_id:
                            img_ids = img_id.split(",")
                            if flag_id in img_ids:
                                for img in img_ids:
                                    img_url = f"https://storage.googleapis.com/afs-prod/media/{img}/1000.jpeg"
                                    dec = re.findall(f'"id":"{img}","type":"Photo","caption":"(.*?)","order"',
                                                     response.text)
                                    if dec:
                                        dec = dec[0].replace("<p>", "").replace("</p>", "")
                                    dic = {"type": "image",
                                           "name": None,
                                           "md5src": self.get_md5_value(img_url) + '.jpg',
                                           "description": dec.replace("\\u003cp>", "").strip() if dec else None,
                                           "src": img_url
                                           }
                                    content.append(dic)

        news_tags = response.xpath('//div[@class="Article"]/*')
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
