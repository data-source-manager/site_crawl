# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class KR_kaomsParser(BaseParser):
    name = 'kr_kaoms'
    
    # 站点id
    site_id = "3eadd75b-eff4-421a-9504-df605c71c075"
    # 站点名
    site_name = "韩国军事研究会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "3eadd75b-eff4-421a-9504-df605c71c075", "source_name": "韩国军事研究会", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("60899564-c45d-3ea4-8092-c64e021e7bc2", "会议厅", "", "政治"),
            ("4a8eaa3e-fe6f-11ec-a30b-d4619d029786", "会议厅/专栏", "http://www.kaoms.or.kr/photo/list.asp", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "list.asp" in response.url:
            news_urls = response.xpath('//div[@class="cover2"]')
            if news_urls:
                for news_url in news_urls:
                    rsp_url = news_url.xpath('./h3/a/@href').get()
                    author = news_url.xpath('./ul/li[1]/text()').get()
                    rsp_author = re.findall('작성자 : (.*)', author)[0]
                    url = urljoin(response.url, rsp_url)
                    self.Dict[url] = {"url": rsp_url, "author": rsp_author}
                    yield url
            else:
                news_urls = response.xpath('//div[@class="items"]/a/@href').extract() or ""
                if news_urls:
                    for news_url in list(set(news_urls)):
                        yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "photo" in response.url:
            title = response.xpath('//table[@class="tb-write"]//tr/th/text()').extract_first(default="")
        else:
            title = response.xpath('//div[contains(@class,"year-cnt")]/button/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        if "photo" in response.url:
            authors = self.Dict[response.url]["author"]
            return authors
        else:
            return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "photo" in response.url:
            time_ = response.xpath('//span[@class="letter-s1"]/text()').extract_first()
            if time_:
                pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response, media_type=None) -> list:
        content = []

        if "photo" in response.url:
            news_tags = response.xpath('//tr[3]/td/div[2]/*|//iframe[contains(@src,"youtube")]')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "b"]:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                    if news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            con_text = self.parseOnetext(con)
                            if con_text:
                                content.extend(con_text)
                    if news_tag.root.tag == "iframe":
                        con_file = self.parse_media(response, news_tag, media_type)
                        if con_file:
                            content.append(con_file)

                    if news_tag.root.tag == "img":
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)
        else:
            img_list = response.xpath('//div[@class="business-cnt active"]')
            if img_list:
                for img in img_list:
                    con_img = self.parse_img(response, img)
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
        videoUrl = news_tag.xpath("./@src").extract_first()
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
        read_count = 0
        read_count_str = response.xpath('//td[@class="tl"]/div[@class="row10"]/text()').getall()
        if read_count_str:
            read_count = int(re.findall('조회수 : (.*)', read_count_str[3])[0])
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
