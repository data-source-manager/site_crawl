# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

import requests
from lxml import etree

from site_crawl.spiders.parser.base_parser import BaseParser
from util.site_deal.interface_helper import facebook_like_count_interface
from util.time_deal import datetime_helper, translatetTime

"""
    模版
"""


class TH_banmuangParser(BaseParser):
    name = 'th_banmuang'
    
    # 站点id
    site_id = "e4d85358-04c5-41bf-83fd-0065bb4f33ed"
    # 站点名
    site_name = "国家报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e4d85358-04c5-41bf-83fd-0065bb4f33ed", "source_name": "国家报", "direction": "th", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("44282538-cba1-44db-9dcf-79f874aa2d5a", "政治", "https://www.banmuang.co.th/news/politic", "政治"),
            ("afeb59e8-ec0b-4675-bd59-e4e7ca43b8e4", "犯罪", "https://www.banmuang.co.th/news/crime", "政治"),
            ("f735aada-d6eb-40fe-8ffe-81b00ec91400", "经济", "https://www.banmuang.co.th/news/economy", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        if "politic" in response.url:
            url = "https://www.banmuang.co.th/news/ajax/politic/1/301485:301439:301410:301401"
            res = requests.get(url)
            response = etree.HTML(res.text)
            news_urls = response.xpath('//div[@class="block list"]//li/a/@href')
            if news_urls:
                for news_url in news_urls:
                    yield news_url
        elif "crime" in response.url:
            url = "https://www.banmuang.co.th/news/ajax/crime/1/301500:301494:301490:301403"
            res = requests.get(url)
            response = etree.HTML(res.text)
            news_urls = response.xpath('//div[@class="block list"]//li/a/@href')
            if news_urls:
                for news_url in news_urls:
                    yield news_url
        elif "economy" in response.url:
            url = "https://www.banmuang.co.th/news/ajax/economy/1/301524:301511:301510:301506"
            res = requests.get(url)
            response = etree.HTML(res.text)
            news_urls = response.xpath('//div[@class="block list"]//li/a/@href')
            if news_urls:
                for news_url in news_urls:
                    yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="block details"]/h3/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        times_ = response.xpath('//div[@class="time"]/text()').extract_first()
        day, month, year, m_time = re.findall('(\d{1,2}) (.*?)(\d{4}).*?(\d{1,2}.\d{1,2})', times_)[0]
        months = re.findall('(.*?) พ.ศ.', month)[0]
        m_times = m_time.replace('.', ':')
        pub_times = translatetTime.thyearDict[year] + "-" + translatetTime.thDict[months] + "-" + day + ' ' + m_times
        if pub_times:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub_times)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="detail img-detail"]/img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//div[@class="detail"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
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
        img = news_tag.xpath('./@data-src').extract_first()
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
        like_count = facebook_like_count_interface(response.url,
                                                   '//td[@class="_51m- hCent _51mw"]//span[@class="_5n6h _2pih/text()"]')
        return like_count

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
