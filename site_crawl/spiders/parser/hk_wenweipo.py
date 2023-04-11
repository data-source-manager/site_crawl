# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser

"""
    模版
"""


class HkWenweipoParser(BaseParser):
    name = 'wenweipo'
    
    # 站点id
    site_id = "03eca8e0-bd46-45ec-8780-dc5b7fcf662e"
    # 站点名
    site_name = "文汇网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "03eca8e0-bd46-45ec-8780-dc5b7fcf662e", "source_name": "文汇网", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("bc083515-2d69-b813-e880-e19fa55f70f7", "专题", "", "政治"),
            ("4a8bfc80-fe6f-11ec-a30b-d4619d029786", "专题/2021香港立法会选举", "https://www.wenweipo.com/spec/gatspecial/electionHKVideo", "政治"),
            ("4a8bfc12-fe6f-11ec-a30b-d4619d029786", "专题/俄乌冲突", "https://www.wenweipo.com/spec/specInternational/UkraineConflictNews", "政治"),
            ("4a8bfac8-fe6f-11ec-a30b-d4619d029786", "台湾", "https://www.wenweipo.com/todaywenwei/whTW", "政治"),
            ("4a8bfb40-fe6f-11ec-a30b-d4619d029786", "国际", "https://www.wenweipo.com/todaywenwei/whinternational", "政治"),
            ("4a8bfba4-fe6f-11ec-a30b-d4619d029786", "评论", "https://www.wenweipo.com/comment/commentcomment", "政治"),
            ("4a8bfa5a-fe6f-11ec-a30b-d4619d029786", "香港", "https://www.wenweipo.com/todaywenwei/whHK", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[contains(@class,"story-item-title")]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1/text()').extract_first(default="")
        if "|" in title:
            title = title.split("|")[1]
        if "】" in title:
            title = title.split("】")[1]
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//div[@class="post-header"]//time/text()').extract_first()
        if time_:
            return time_

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="post-body"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "figure":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

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
