# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    站点解析模版
"""


class HkStheadlineParser(BaseParser):
    name = 'stheadline'
    
    # 站点id
    site_id = "c4b2b834-1b74-11ec-9dd8-6030d461e866"
    # 站点名
    site_name = "星岛日报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c4b2b834-1b74-11ec-9dd8-6030d461e866", "source_name": "星岛日报", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("d7ec979d-41df-3157-b3e3-ad6b09528960", "即时", "", "政治"),
            ("8ad558d5-e4a3-4692-867f-82481a1e37c7", "即时/中国", "https://std.stheadline.com/realtime/china/%E5%8D%B3%E6%99%82-%E4%B8%AD%E5%9C%8B", "政治"),
            ("57638348-b57e-4658-9ed1-ef3c5b6165a5", "即时/国际", "https://std.stheadline.com/realtime/international/%E5%8D%B3%E6%99%82-%E5%9C%8B%E9%9A%9B", "政治"),
            ("e7002c66-7607-11ed-ad4d-d4619d029786", "即时/港闻", "https://std.stheadline.com/realtime/hongkong/%E5%8D%B3%E6%99%82-%E6%B8%AF%E8%81%9E", "政治"),
            ("180c48b1-4533-3cc6-b404-a9a9970c90b8", "日报", "", "政治"),
            ("f687e849-6219-4593-8d6c-949c3315caed", "日报/中国", "https://std.stheadline.com/daily/china/%E6%97%A5%E5%A0%B1-%E4%B8%AD%E5%9C%8B", "政治"),
            ("4a8de0e0-fe6f-11ec-a30b-d4619d029786", "日报/国际", "https://std.stheadline.com/daily/international/%E6%97%A5%E5%A0%B1-%E5%9C%8B%E9%9A%9B", "政治"),
            ("4a8ddfd2-fe6f-11ec-a30b-d4619d029786", "日报/港闻", "https://std.stheadline.com/daily/hongkong/%E6%97%A5%E5%A0%B1-%E6%B8%AF%E8%81%9E", "政治"),
            ("4a8ddeb0-fe6f-11ec-a30b-d4619d029786", "日报/社论", "https://std.stheadline.com/daily/editorial/%E6%97%A5%E5%A0%B1-%E7%A4%BE%E8%AB%96", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "c4b2b834-1b74-11ec-9dd8-6030d461e866"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="col-md-9"]//a[contains(@class,"title")]/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//header/h1/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[@class="date"]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="video paragraphs medium"]/*|'
                                   '//div[@class="video paragraphs medium"]/text()')
        if news_tags:
            for news_tag in news_tags:
                if type(news_tag.root) == str:
                    if news_tag.root.strip():
                        content.append({
                            "type": "text",
                            "data": news_tag.root
                        })
                else:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                        if news_tag.xpath("./article"):
                            for tag in news_tag.xpath('./article'):
                                con_img = self.parse_img(response, tag)
                                if con_img:
                                    content.append(con_img)
                        elif news_tag.xpath("./figure"):
                            con_img = self.parse_img(response, news_tag)
                            if con_img:
                                content.append(con_img)
                        else:
                            text_dict = self.parseOnetext(news_tag)
                            if text_dict:
                                if "《星島頭條》APP" not in text_dict[0].get("data"):
                                    content.extend(text_dict)

                    if news_tag.root.tag == "figure":
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        dic = {}
        if cons:
            if new_cons:
                dic['data'] = "".join(cons).strip()
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
            if img.startswith("data:image/gif;base64"):
                return {}
            img_url = urljoin(response.url, img)
            des = "".join(news_tag.xpath('.//figcaption//text()').extract()).strip()
            if not des:
                des = news_tag.xpath('.//img/@alt').extract_first()
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": des,
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
        videoUrl = news_tag.xpath("./@src").extract_first()
        suffix = f".{media_type}"

        video_dic = {}

        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }

            if suffix == ".mp3":
                video_dic["type"] = "audio"
            elif suffix == ".mp4":
                video_dic["type"] = "video"

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
