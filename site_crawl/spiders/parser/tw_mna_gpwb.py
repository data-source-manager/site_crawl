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


class TwGpwbParser(BaseParser):
    name = 'gpwb'
    
    # 站点id
    site_id = "a8293217-c155-4d44-bea7-5bfea631fa01"
    # 站点名
    site_name = "军事新闻通讯社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "a8293217-c155-4d44-bea7-5bfea631fa01", "source_name": "军事新闻通讯社", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b93e4-fe6f-11ec-a30b-d4619d029786", "军事相簿", "https://mna.gpwb.gov.tw/photo/", "政治"),
            ("4a8b92ea-fe6f-11ec-a30b-d4619d029786", "军文总览", "https://mna.gpwb.gov.tw/news/overview/", "政治"),
            ("4a8b9376-fe6f-11ec-a30b-d4619d029786", "影音专区", "https://mna.gpwb.gov.tw/video/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.title = {}

    def parse_list(self, response) -> list:
        if "video" in response.url:
            news_urls = response.xpath('//div[@class="blk"]/a')
            if news_urls:
                for news_url in news_urls:
                    video_url = news_url.xpath("./@data-target").extract_first()
                    complete_url = "https://youtu.be/" + video_url.replace("#", "").strip()
                    video_title = news_url.xpath("./@title").extract_first()
                    self.title[video_url.replace("#", "").strip()] = video_title
                    yield complete_url
        else:
            news_urls = response.xpath('//div[contains(@class,"annexBlk")]/ul/li/a/@href').extract() or ""
            if news_urls:
                for news_url in news_urls:
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "youtu.be" in response.url:
            key = re.findall('v=(.*?)&', response.url)[0]
            return self.title[key]
        if "news" in response.url:
            title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
            if "-" in title:
                title = title.split("-")[0]
            return title.strip() if title else ""
        else:
            title = response.xpath('//meta[@name="title"]/@content').extract_first(default="")
            return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "photos" in response.url:
            pub_time = '//meta[@property="og:updated_time"]/@content'
            time_ = response.xpath(pub_time).extract_first()
            if time_:
                pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        elif "news" in response.url:
            pub_time = '//div[@class="info"]/ul/li/text()'
            if "民國" in pub_time:
                pub_time = pub_time.replace("民國", "")
                pub_res = re.findall("\d+", pub_time)
                pub_res[0] = twYearDict[pub_res[0]]
                time_ = "-".join(pub_res)
                if time_:
                    pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        if "photos" in response.url:
            for x in response.xpath('//div[contains(@class,"photo-list-view")]/div/@style').extract():
                img_url = urljoin(response.url, re.findall('url\((.*?)\)', x)[0])
                dic = {"type": "image",
                       "name": None,
                       "md5src": self.get_md5_value(img_url) + '.jpg',
                       "description": None,
                       "src": img_url
                       }
                content.append(dic)
        elif "youtu.be" in response.url:
            video_url = response.xpath('//meta[@property="og:video:url"]/@content').extract_first()
            video_dic = {
                "type": "video",
                "src": video_url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_url) + ".mp4"
            }
            content.append(video_dic)

        elif "news" in response.url:
            news_tags = response.xpath('//div[@class="containerBlk"]/article/*')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                        text_dict = self.parse_text(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                    if news_tag.root.tag == "figure":
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)
        return content

    def get_detected_lang(self, response) -> str:
        return "ko"

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
