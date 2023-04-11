# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class KrSejongParser(BaseParser):
    name = 'sejong'
    
    # 站点id
    site_id = "04904825-9f25-404d-b06e-40f997c8d849"
    # 站点名
    site_name = "世宗研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "04904825-9f25-404d-b06e-40f997c8d849", "source_name": "世宗研究所", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8bd8c2-fe6f-11ec-a30b-d4619d029786", "世宗政策研究", "https://sejong.org/web/boad/1/egolist.php?bd=13", "政治"),
            ("4a8bd78c-fe6f-11ec-a30b-d4619d029786", "世宗解说", "https://sejong.org/web/boad/1/egolist.php?bd=1", "政治"),
            ("2d92e0ed-87a0-8147-088d-e363756ec1e1", "刊物", "", "政治"),
            ("62971893-0ae4-4d86-9228-d35d117fd19a", "刊物/世宗政策简报", "https://sejong.org/web/boad/1/egolist.php?bd=3", "政治"),
            ("f6e66e2f-8f49-4bb9-9493-b1d5422ffd9c", "刊物/国家战略", "https://sejong.org/web/boad/1/egolist.php?bd=3", "政治"),
            ("4a8bd854-fe6f-11ec-a30b-d4619d029786", "国家战略", "https://sejong.org/web/boad/1/egolist.php?bd=15", "政治"),
            ("4a8bd69c-fe6f-11ec-a30b-d4619d029786", "形势与政策", "https://sejong.org/web/boad/1/egolist.php?bd=2", "政治"),
            ("4a8bd7f0-fe6f-11ec-a30b-d4619d029786", "研究报告", "https://sejong.org/web/boad/1/egolist.php?bd=56", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "04904825-9f25-404d-b06e-40f997c8d849"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//p[@class="lt_tit pb15"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="title"]/@content').extract_first(default="")
        if "]" in title and title.strip().startswith("["):
            title = title.split("]")[1]
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//div[@class="view_w"]//span[contains(@class,"date")]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_.strip())
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="view_bx04"]/div/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
        file = response.xpath('//div[@class="view_bx02"]//a')
        if file:
            con_video = self.parse_file(response, file)
            if con_video:
                content.append(con_video)

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
            oneCons = "".join(cons).strip().replace('\u200b', '').replace('\xa0', '')
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
                "name": news_tag.xpath('./span/text()').extract_first().strip(),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("./@href").extract_first()
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": news_tag.xpath('./span/text()').extract_first().strip(),
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
        read = response.xpath('//div[@class="view_w"]//span[contains(@class,"hit")]/text()').extract_first()
        return read.strip() if read else 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
