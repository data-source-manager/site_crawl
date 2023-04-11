# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class JpYahooParser(BaseParser):
    name = 'yahoo'
    
    # 站点id
    site_id = "42f09e21-dcaa-430d-b911-253832f07af1"
    # 站点名
    site_name = "Yahoo奇摩日本网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "42f09e21-dcaa-430d-b911-253832f07af1", "source_name": "Yahoo奇摩日本网", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91233dc8-2f72-11ed-a768-d4619d029786", "国内", "https://news.yahoo.co.jp/categories/domestic", "政治"),
            ("91233df0-2f72-11ed-a768-d4619d029786", "国际", "https://news.yahoo.co.jp/categories/world", "政治"),
            ("91233e22-2f72-11ed-a768-d4619d029786", "经济", "https://news.yahoo.co.jp/categories/business", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    """
    @fix: liyun 2023-01-06 -> 过滤非目标域名的news_url
    """

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//li[@class=" yjnSub_list_item"]/a/@href').extract() or []
        for news_url in news_urls:
            if news_url.startswith("https://news.yahoo.co.jp"):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="sc-likbZx kbaEPj"]/text()|//article/header/h1/text()').extract_first(
            default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="twitter:author"]/@content').extract()
        if authors:
            for au in author_list:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@name="pubdate"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="sc-ipZHIp immNQd"]/a')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))

        news_tags = response.xpath('//div[@class="sc-iBEsjs hJPyKg"]/p|'
                                   '//article/div[contains(@class,"article_body")]/div/div|'
                                   '//article/div[contains(@class,"article_body")]/div/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "div":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "ja"

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

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.xpath('.//p/text()').extract_first(),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.attrib.get('alt'),
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
