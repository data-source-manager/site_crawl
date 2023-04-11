# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import requests

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class SG_govParser(BaseParser):
    name = 'sg_gov'
    
    # 站点id
    site_id = "3b2a7a7f-fe94-4688-ba5b-5024d0ad33ba"
    # 站点名
    site_name = "新加坡政府"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "3b2a7a7f-fe94-4688-ba5b-5024d0ad33ba", "source_name": "新加坡政府", "direction": "sg", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9123709a-2f72-11ed-a768-d4619d029786", "国防和安全", "https://www.gov.sg/defence-and-security", "政治"),
            ("912370cc-2f72-11ed-a768-d4619d029786", "外交事务", "https://www.gov.sg/foreign-affairs", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "defence" in response.url:
            res_url = 'https://www.gov.sg/api/v1/search?fq=contenttype_s:[*%20TO%20*]&fq=isfeatured_b:false&fq=primarytopic_s:%22Defence%20and%20Security%22%20OR%20secondarytopic_sm:%22Defence%20and%20Security%22&q=*:*&sort=publish_date_tdt%20desc&start=0&rows=10'
        else:
            res_url = 'https://www.gov.sg/api/v1/search?fq=contenttype_s:[*%20TO%20*]&fq=isfeatured_b:false&fq=primarytopic_s:%22Foreign%20Affairs%22%20OR%20secondarytopic_sm:%22Foreign%20Affairs%22'
        Json_data = requests.get(res_url).json()
        for docs in Json_data['response']['docs']:
            item_url = "https://www.gov.sg" + docs['pageurl_s']
            pub_time = docs['publishdate_s']
            header_img = "https://www.gov.sg" + docs['imageurl_s']
            self.Dict[item_url] = {"dt": pub_time, 'img': header_img}
            yield item_url

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='banner-content__title']/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = self.Dict[response.url]['dt']
        if datePublished_str:
            dt = datetime_helper.fuzzy_parse_timestamp(datePublished_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags_node = response.xpath("//a[@class='button is-radiusless tag tag-primary']/text()").getall()
        if tags_node:
            for tags in tags_node:
                tags_list.append(tags.strip())
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='component content']/*")
        header_img = self.Dict[response.url]['img']
        if header_img:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(header_img) + '.jpg',
                   "description": None,
                   "src": header_img}
            content.append(dic)
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h3", "h5", "span", "p", "blockquote"] and news_tag.root.get("class",
                                                                                                      "") != 'article-meta':
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src", img_des="./@alt")
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
        """"
            可以对一个标签下存在多个段落进行解析
        """
        dic = {}
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'

        return dic

    def parse_img(self, response, news_tag, img_xpath='', img_des=''):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath(img_xpath).extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(img_des).extract_first() or None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath("./self::a[contains(@href,'.pdf')]/@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.xpath("./self::a[contains(@href,'.pdf')]/text()").get() or None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath(".//iframe/@src").extract_first()
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
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        return comment_count

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
