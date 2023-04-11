# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal.datetime_helper import parseTimeWithOutTimeZone

"""
    模版
"""


class TW_aarocParser(BaseParser):
    name = 'tw_aaroc'
    
    # 站点id
    site_id = "36493179-7f52-4a0c-95e6-d1a209b0e9ca"
    # 站点名
    site_name = "陆军专科学校"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "36493179-7f52-4a0c-95e6-d1a209b0e9ca", "source_name": "陆军专科学校", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("00a73c8a-7c80-4d1f-a0cd-bba417b10f4a", "最新消息", "https://www.aaroc.edu.tw/news/191/10000/24282", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath('//tr[contains(@id,"DXDataRow")]')
        if news_items:
            for news_item in news_items:
                rsp_url = news_item.xpath('./td/a/@href').get()
                rsp_time = news_item.xpath('./td[@class="dxgv"]/text()').get()
                url = urljoin(response.url, rsp_url)
                self.dict[url] = {"time": rsp_time}
                yield url

    def get_title(self, response) -> str:
        title = response.xpath('//ol[@class="breadcrumb"]/li/a/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = self.dict[response.url]["time"]
        if time_:
            dateTime = datetime.strptime(time_.replace("T", " ").strip(), "%Y/%m/%d")
            return parseTimeWithOutTimeZone(dateTime, site_name="陆军专科学校")

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="cMaster"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    if news_tag.xpath(".//img"):
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parse_text(con)
                        if con_text:
                            content.append(con_text)
                if news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
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
        if img.startswith("data:image/gif;base64"):
            return {}
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

    def parse_media(self, response, news_tag, media_type):
        videoUrl = news_tag.xpath("").extract_first()
        if media_type == "video":
            suffix = ".mp4"
        else:
            suffix = ".mp3"
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
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
