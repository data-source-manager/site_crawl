# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.time_deal.translatetTime import twYearDict

"""
    模版
"""


class TwEyParser(BaseParser):
    name = 'ey'
    # 站点id
    site_id = "928acb6e-9a3f-44ad-b717-8561d4dbce05"
    # 站点名
    site_name = "台湾行政院全球资讯网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "928acb6e-9a3f-44ad-b717-8561d4dbce05", "source_name": "台湾行政院全球资讯网", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("b8a9a126-c12e-485f-b06f-05dd75334840", "影音快讯", "https://www.ey.gov.tw/Page/EC244A0C9634ED65", "政治"),
            ("38ce2446-c633-40d5-b559-e095114b2235", "政策与计划", "", "政治"),
            ("01562eb9-bb2d-4713-86a2-e89786221cc5", "政策与计划/交通建设", "https://www.ey.gov.tw/Page/A1630AEAED66C646", "政治"),
            ("c690d576-d431-46f7-80c9-4fc13c26be33", "政策与计划/内政及国土", "https://www.ey.gov.tw/Page/94CCDEAAE8F7D325", "政治"),
            ("6d4357d8-9184-432d-af4d-671c18c5eabf", "政策与计划/农业环保", "https://www.ey.gov.tw/Page/398D5360E5590B53", "政治"),
            ("3732eae4-ae3b-46a5-b6d0-4214e47bc805", "政策与计划/卫生福利劳动", "https://www.ey.gov.tw/Page/68ECAA3C76C67678", "政治"),
            ("6cdc7b4b-20bc-4231-9eef-5ddebc7e8d83", "政策与计划/外交国防", "https://www.ey.gov.tw/Page/37DB6ED8BE2E6C8", "政治"),
            ("7ff9c689-c400-4efd-8183-687b51c23d78", "政策与计划/政策橱窗", "https://www.ey.gov.tw/Page/D4EE9698E2D8FC64", "政治"),
            ("18f4d960-b513-4cee-a3b7-7cd6b689f63e", "政策与计划/教育文化及科技", "https://www.ey.gov.tw/Page/EC2BA62464527A0C", "政治"),
            ("98c5638e-8a74-4cca-a490-af5202386cad", "政策与计划/施政方针与报告", "https://www.ey.gov.tw/Page/5C208DA85C814C47", "政治"),
            ("6cda4404-de66-4f7e-8fa1-995b72600ace", "政策与计划/法务", "https://www.ey.gov.tw/Page/B75C748A1E8045F5", "政治"),
            ("a9efd02b-7f49-4632-8c9d-d08c02f033f5", "政策与计划/综合行政", "https://www.ey.gov.tw/Page/96743BD48A8F0518", "政治"),
            ("460723d0-0756-46e4-a807-ccbca1bf4267", "政策与计划/财政经济", "https://www.ey.gov.tw/Page/F676CAEFDF9D3A61", "政治"),
            ("20d4f928-e611-44f7-80cd-f92535d53ef6", "政策与计划/院会议案", "https://www.ey.gov.tw/Page/B572E2F7D8DF5CE1", "政治"),
            ("def0a276-7e29-3a3b-af98-55a115a04b8c", "新闻与公告", "", "政治"),
            ("e7009688-7607-11ed-ad4d-d4619d029786", "新闻与公告/本院新闻", "https://www.ey.gov.tw/Page/6485009ABEC1CB9C", "政治"),
            ("154f792e-9ab7-4775-bbc2-5d1d6ec15327", "新闻与公告/行政院会议", "https://www.ey.gov.tw/Page/AE4885326ADF43DD", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.detail = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//ul[contains(@class,"list-group-item")]/li//a|'
                                   '//ul[@id="grid"]/li//a|'
                                   '//div[contains(@class,"video_box")]//iframe')
        if news_urls:
            for news_url in news_urls:
                href = news_url.xpath("./@href").extract_first()
                if not href:
                    href = news_url.xpath("./@src").extract_first()

                url = urljoin(response.url, href)
                if "www.ey.gov.tw" in url:
                    if self.channel[0]["site_board_name"] == "政策与计划/施政方针与报告":
                        self.detail[url] = {
                            "title": news_url.xpath("./@title").extract_first().replace(".pdf", ""),
                            "pub": news_url.xpath("./span[@class='date']/text()").extract_first()
                        }
                        yield url
                    elif self.channel[0]["site_board_name"] == "影音快讯":
                        self.detail[url] = {"title": news_url.xpath('./@title').extract_first(),
                                            "pub": news_url.xpath("../following-sibling::span[1]").extract_first()}
                        yield url
                    else:
                        yield url

    def get_title(self, response) -> str:
        if 'https://www.ey.gov.tw/File' in response.url or "www.youtube.com" in response.url:
            return self.detail[response.url]["title"]
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "www.youtube.com" in response.url or "www.ey.gov.tw/File" in response.url:
            time_ = self.detail[response.url]["pub"]
        else:
            time_ = response.xpath('//span[@class="date_style2"]/font/text()|'
                                   '//span[@class="date_style2"]/span/text()').extract_first()
        if time_:
            if "：" in time_:
                time_ = time_.split('：')[1]

            time_list = time_.split("-")
            time_list[0] = twYearDict[time_list[0]]
            time_ = "-".join(time_list)
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        if "www.youtube.com" in response.url:
            video_src = response.url
            return [{
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + ".mp4"
            }]
        elif "www.ey.gov.tw/File" in response.url:
            file_src = response.url
            return [{
                "type": "file",
                "src": file_src,
                "name": self.detail.get(file_src).get("title"),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }]
        else:
            news_tags = response.xpath('//div[contains(@class,"words_content")]/div/*|'
                                       '//div[contains(@class,"words_content")]/*')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                    if news_tag.root.tag == "ul":
                        con_img = self.parse_img(response, news_tag.xpath(".//img"))
                        if con_img:
                            content.append(con_img)
                        for x in news_tag.xpath("./li"):
                            con_text = self.parseOnetext(x)
                            if con_text:
                                content.append(con_text)
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
