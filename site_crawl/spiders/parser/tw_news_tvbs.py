# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.time_deal.translatetTime import twYearDict

"""
    模版
"""


class TwTvbsParser(BaseParser):
    name = 'tvbs'
    
    # 站点id
    site_id = "24dff00e-75d4-4a41-b75b-2413ef1b569c"
    # 站点名
    site_name = "TVBS新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "24dff00e-75d4-4a41-b75b-2413ef1b569c", "source_name": "TVBS新闻", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e7008f3a-7607-11ed-ad4d-d4619d029786", "全球", "https://news.tvbs.com.tw/world", "政治"),
            ("e700e71e-7607-11ed-ad4d-d4619d029786", "国内", "https://news.tvbs.com.tw/pack/packdetail/667", "政治"),
            ("e700565a-7607-11ed-ad4d-d4619d029786", "政治", "https://news.tvbs.com.tw/politics", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.title = {}
        self.time = {}

    def parse_list(self, response) -> list:
        if "pack" in response.url:
            xpath = '//article//div[@class="list"]/ul/li/a/@href'
            news_urls = response.xpath(xpath).extract() or ""
            if news_urls:
                for news_url in news_urls:
                    yield urljoin(response.url, news_url)
        # pdf
        elif "poll-center" in response.url:
            news_urls = response.xpath('//div[@class="company_content_table1"]/table//tr')[1:]
            if news_urls:
                for news_url in news_urls:
                    pub = news_url.xpath('./td[1]/text()').extract_first()
                    url = news_url.xpath('./td/a/@href').extract_first()
                    title = news_url.xpath('./td/a/text()').extract_first()
                    self.title[url] = title
                    self.time[url] = pub
                    yield url
        else:
            news_urls = response.xpath('//div[@class="news_now2"]//ul/li/a/@href|'
                                       '//div[@class="list"]/ul/li/a/@href').extract() or ""
            if news_urls:
                for news_url in news_urls:
                    if "word" in news_url or "politic" in news_url:
                        yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if response.url.endswith(".pdf"):
            return self.title[response.url]
        title = response.xpath('//meta[@app="tvbsapp"]/@newstitle').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        if response.url.endswith(".pdf"):
            return []

        authors = response.xpath('//div[@class="author"]/a/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if response.url.endswith(".pdf"):
            pub = self.time[response.url]
            if time:
                pub = re.findall("\d+", pub)
                pub[0] = twYearDict[pub[0]]
                time_ = "-".join(pub)
                if time_:
                    pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
                return "9999-01-01 00:00:00"
        else:
            time_ = response.xpath('//meta[@name="pubdate"]/@content').extract_first()
            if time_:
                pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        if response.url.endswith(".pdf"):
            return []
        tags = response.xpath('//meta[@itemprop="keywords"]/@content').extract_first()
        if tags:
            if "," in tags:
                tags = tags.split(",")
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        if response.url.endswith(".pdf"):
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
            return content
        else:
            img_list = response.xpath('//div[@class="img_box"]/div')
            if img_list:
                for img in img_list:
                    con_img = img.xpath(".//img/@src").extract_first()
                    if con_img:
                        dic = {"type": "image",
                               "name": None,
                               "md5src": self.get_md5_value(con_img) + '.jpg',
                               "description": "".join(img.xpath('.//img/@alt').extract()).strip(),
                               "src": con_img
                               }
                        content.append(dic)

            news_tags = response.xpath('//div[@class="article_content"]/text()|'
                                       '//div[@class="article_content"]/div[contains(@class,"img")]|'
                                       '//div[@class="article_content"]/div[@id="first_p"]/p')
            if news_tags:
                for news_tag in news_tags:
                    if type(news_tag.root) == str:
                        con = news_tag.root
                        if con.strip():
                            content.append({
                                "data": con.strip(),
                                "type": "text"
                            })
                    else:
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
        img = news_tag.xpath('.//img/@data-original').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//img/@alt').extract()).strip(),
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
