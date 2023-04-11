# -*- coding: utf-8 -*-
# update:(liyun:2023-01-13) -> 新增板块
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwPollsParser(BaseParser):
    name = 'polls'
    
    # 站点id
    site_id = "767076cb-d0b7-41e0-a197-c249f7bb5130"
    # 站点名
    site_name = "趋势民调"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "767076cb-d0b7-41e0-a197-c249f7bb5130", "source_name": "趋势民调", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("fef0786c-68ce-4ce2-82f2-a7f2b7a635dd", "网络大数据", "", "政治"),
            ("7b43db4b-66e4-48b0-b0a2-21780db9daed", "网络大数据/政治大数据", "https://polls.com.tw/data_tax/%e6%94%bf%e6%b2%bb%e5%a4%a7%e6%95%b8%e6%93%9a/", "政治"),
            ("233e5277-6cdd-451e-be3a-c63ce5117280", "网络大数据/时事大数据", "https://polls.com.tw/data_tax/%e6%99%82%e4%ba%8b%e5%a4%a7%e6%95%b8%e6%93%9a/", "政治"),
            ("f70f2e8f-ca7e-4114-a5d1-7e875829605e", "网络大数据/金融大数据", "https://polls.com.tw/data_tax/%e9%87%91%e8%9e%8d%e5%a4%a7%e6%95%b8%e6%93%9a/", "政治"),
            ("4a8c3ae2-fe6f-11ec-a30b-d4619d029786", "调查指标", "https://polls.com.tw/target/", "政治"),
            ("b0e7e6ac-93b0-42d3-ac66-1ea2a67f87c0", "调查新闻", "https://polls.com.tw/news/", "政治"),
            ("8f40f994-e07a-4ca3-aaf1-52e7ef9af2f6", "调查新闻/产业调查", "https://polls.com.tw/news_tax/%e7%94%a2%e6%a5%ad%e8%aa%bf%e6%9f%a5/", "政治"),
            ("fcf37bd0-c4da-4af3-9472-47840490b4ed", "调查新闻/全球民调", "https://polls.com.tw/news_tax/%e5%85%a8%e7%90%83%e6%b0%91%e8%aa%bf/", "政治"),
            ("4eed770e-be9b-499c-8c31-5bb91bfbfe8e", "调查新闻/国内政情", "https://polls.com.tw/news_tax/domestic-politics/", "政治"),
            ("8c05d433-83be-4fcb-8f96-26d3b0f49f2a", "调查新闻/总统大选", "https://polls.com.tw/news_tax/%e7%b8%bd%e7%b5%b1%e5%a4%a7%e9%81%b8/", "政治"),
            ("4a8c3a7e-fe6f-11ec-a30b-d4619d029786", "调查评论", "https://polls.com.tw/comment/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//ul[contains(@class,"uk-margin-medium-bottom")]/li/a[contains(@href,"polls")]/@href').extract()
        if news_urls:
            for news_url in list(set(news_urls)):
                if "page" in news_url:
                    continue
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[contains(@class,"heading-default")]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@property="article:author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//ul[@class="uk-flex uk-flex-wrap"]/li/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="entry-content"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "blockquote"]:
                    if news_tag.root.tag == "blockquote":
                        news_tag = news_tag.xpath('./p')
                    if news_tag.xpath('.//img').extract():
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)
                        continue
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)

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
            suffix = img_url.split(".")[-1].lower()
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + f'.{suffix}',
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
        read = response.xpath('//span[@class="post-views-count"]/text()').extract_first()
        return int(read.replace(",", "").strip()) if read else 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
