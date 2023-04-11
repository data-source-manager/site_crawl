# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class USA_natoParser(BaseParser):
    name = 'usa_nato'
    
    # 站点id
    site_id = "1b6f7f54-ff50-4d8c-93b6-cea1cf7a9e08"
    # 站点名
    site_name = "北大西洋公约组织"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "1b6f7f54-ff50-4d8c-93b6-cea1cf7a9e08", "source_name": "北大西洋公约组织", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8ec334-fe6f-11ec-a30b-d4619d029786", "出版物", "https://www.nato.int/cps/en/natohq/79511.htm", "政治"),
            ("4a8ec276-fe6f-11ec-a30b-d4619d029786", "新闻稿", "https://www.nato.int/cps/en/natohq/press_releases.htm", "政治"),
            ("4a8ec2d0-fe6f-11ec-a30b-d4619d029786", "消息", "https://www.nato.int/cps/en/natohq/news.htm", "政治"),
            ("4a8ec38e-fe6f-11ec-a30b-d4619d029786", "演讲", "https://www.nato.int/cps/en/natohq/opinions.htm", "政治"),
            ("4a8ec21c-fe6f-11ec-a30b-d4619d029786", "音频", "https://www.nato.int/cps/en/natohq/audio.htm", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}
        self.dict = {}

    def parse_list(self, response) -> list:
        if "79511.htm" in response.url:
            news_urls = response.xpath('//div[@class="inner-content "]')
            if news_urls:
                for news_url in news_urls:
                    rsp_url = news_url.xpath('./p/a/@href').get()
                    rsp_time = news_url.xpath('//div[@class="inner-content "]/span[@class="date"]/text()').get()
                    url = urljoin(response.url, rsp_url)
                    self.dict[url] = {"time": rsp_time}
                    yield url
        else:
            news_node = response.xpath('//div[@class="searchresults"]//tbody//tr')
            if news_node:
                for new_node in news_node:
                    rsp_url = new_node.xpath('.//a/@href').get()
                    rsp_time = new_node.xpath('./td[@class="h-no-wrap fs-small"]/text()').get()
                    rsp_title = new_node.xpath('.//h3/text()|.//p/a/text()').get()
                    url = urljoin(response.url, rsp_url)
                    self.Dict[url] = {'time': rsp_time, 'title': rsp_title}
                    yield url

    def get_title(self, response) -> str:
        if "topics_" in response.url:
            title = response.xpath('//h1[@class="fs-huge"]/text()').extract_first(default="")
        else:
            title = self.Dict[response.url]['title']
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "topics_" in response.url:
            time_ = self.dict[response.url]['time']
        else:
            time_ = self.Dict[response.url]['time']
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        if ".mp3" in response.url:
            return content
        else:
            news_tags = response.xpath('//section[@class="content cf"]/*|//div[@class="list-wrapper"]/ul//a|'
                                       '//div[@style="text-align: justify;"]/*|'
                                       '//div[@style="text-align: justify;"]//img')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div", "strong", "b", "blockquote", "pre"]:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                    if news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            con_text = self.parseOnetext(con)
                            if con_text:
                                content.extend(con_text)
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
            oneCons = "".join(cons).strip().replace('\n', '')
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
