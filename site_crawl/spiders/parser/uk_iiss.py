# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class IissParser(BaseParser):
    name = 'iiss'
    
    # 站点id
    site_id = "e8fac082-cd17-6d64-4d1f-c2b76393de8f"
    # 站点名
    site_name = "国际战略研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e8fac082-cd17-6d64-4d1f-c2b76393de8f", "source_name": "国际战略研究所", "direction": "uk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("efa7b14a-02b1-cd8c-5979-68a200d3bad8", "专题", "", "政治"),
            ("4a8bc2b0-fe6f-11ec-a30b-d4619d029786", "专题/全球政治", "https://www.iiss.org/topics/global-politics", "政治"),
            ("4a8bc0f8-fe6f-11ec-a30b-d4619d029786", "专题/冲突", "https://www.iiss.org/topics/conflict", "政治"),
            ("4a8bc238-fe6f-11ec-a30b-d4619d029786", "专题/地缘经济学", "https://www.iiss.org/topics/geo-economics", "政治"),
            ("4a8bc382-fe6f-11ec-a30b-d4619d029786", "专题/恐怖主义与安全", "https://www.iiss.org/topics/terrorism-and-security", "政治"),
            ("4a8bc314-fe6f-11ec-a30b-d4619d029786", "专题/战略、技术和军控", "https://www.iiss.org/topics/strategy-technology-and-arms-control", "政治"),
            ("4a8bc1ca-fe6f-11ec-a30b-d4619d029786", "专题/环境和气候变化", "https://www.iiss.org/topics/environmental-and-climate-change", "政治"),
            ("4a8bc15c-fe6f-11ec-a30b-d4619d029786", "专题/防御", "https://www.iiss.org/topics/defence", "政治"),
            ("4a8bc3f0-fe6f-11ec-a30b-d4619d029786", "研究报告", "https://www.iiss.org/blogs/research-paper", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = re.findall('"Link":"(.*?)",', response.text)
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="twitter:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = re.findall('"contentDate":"(.*?)"', response.text)
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_[0])
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        video = re.findall('{"VideoId":"(.*?)"}', response.text)
        if video:
            video_url = "https://www.youtube.com/embed/{}".format(video[0])
            video_dic = {
                "type": "video",
                "src": video_url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_url) + ".mp4"
            }
            content.append(video_dic)
        news_tags = re.findall('Components.Reading, {"Html":"(.*?)"', response.text)
        if news_tags:
            news_tag = re.sub('<[^<]+?>', '', news_tags[0]).replace('\n', '').strip()
            if "." in news_tag:
                news_tag = news_tag.split(".")
                for con in news_tag:
                    if con.strip():
                        content.append({
                            "data": con.strip(),
                            "type": "text"
                        })

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
