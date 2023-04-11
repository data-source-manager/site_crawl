# -*- coding: utf-8 -*-
import time
from urllib.parse import unquote
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class TwDppParser(BaseParser):
    name = 'dpp'
    # 站点id
    site_id = "eb85dcc5-3d84-4773-945a-4ae3737eb539"
    # 站点名
    site_name = "民进党新闻中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "eb85dcc5-3d84-4773-945a-4ae3737eb539", "source_name": "民进党新闻中心", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("14e91c5c-b65f-3551-94ea-d1fe92804ae0", "下载专区", "https://www.dpp.org.tw/download", "政治"),
            ("4fc5aa8d-a7e3-3fab-9d71-9182ed46ce3c", "影片专区", "https://www.dpp.org.tw/", "政治"),
            ("4a8cbd28-fe6f-11ec-a30b-d4619d029786", "新闻中心", "https://www.dpp.org.tw/media/1", "政治"),
            ("011ca52e-a748-3b16-b242-9c8a5e4dfb29", "最新消息", "https://www.dpp.org.tw/news", "政治"),
            ("b53b98ef-3e07-3773-8917-74616a57c521", "辟谣专区", "https://www.dpp.org.tw/anti_rumor", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "eb85dcc5-3d84-4773-945a-4ae3737eb539"
        self.Dict = {}
        self.DICT = {}

    def parse_list(self, response) -> list:
        if "download" in response.url:
            news_urls = response.xpath('//div[@class="container"]/ul/li')
            if news_urls:
                for news_url in news_urls:
                    rsp_url = news_url.xpath('./p/a/@href').get()
                    rsp_title = news_url.xpath('./h3/text()').get()
                    self.DICT[rsp_url] = {'title': rsp_title}
                    yield rsp_url
        elif response.url.endswith(".tw/"):
            news_urls = response.xpath('//a[@class="various fancybox.iframe"]')
            if news_urls:
                for news_url in news_urls:
                    rsp_url = news_url.xpath('./@href').get()
                    rsp_title = news_url.xpath('./@title').get()
                    self.Dict[rsp_url] = {'title': rsp_title}
                    yield rsp_url
        else:
            news_urls = response.xpath('//h2/a/@href|//a[@class="button"]/@href|//a[@class="news_list"]/@href|'
                                       '//div[@class="event828_news_item"]/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "download" in response.url:
            title = self.DICT[unquote(response.url)]['title']
            return title.strip() if title else ""
        elif "youtube" in response.url:
            title = self.Dict[response.url]['title']
            return title.strip() if title else ""
        else:
            title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
            return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "download" in response.url:
            return "9999-01-01 00:00:00"
        else:
            time_ = response.xpath('//p[@class="news_content_date"]/text()').extract_first()
            if time_:
                pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        if "download" in response.url:
            return tags_list
        else:
            tags = response.xpath('//div[@class="news text-center"]//li/a/text()').extract()
            if tags:
                for tag in tags:
                    if tag.strip():
                        tags_list.append(tag.strip())

            return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        if "download" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
        elif "youtube" in response.url:
            video_dic = {
                "type": "video",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".mp4"
            }
            content.append(video_dic)
        else:
            news_tags = response.xpath('//div[@id="media_contents"]/*|//div[@id="news_contents"]/p/img|'
                                       '//div[@id="news_contents"]/p/a|//div[@id="news_contents"]/*')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                        text_dict = self.parse_text(news_tag)
                        if text_dict:
                            content.extend(text_dict)
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
        return "zh-tw"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath('.//text()').extract() or ""

        new_cons = []

        if cons:
            for con in cons:
                if con.strip():
                    new_cons.append({'data': "".join(con).strip(), 'type': "text"})
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
        img = news_tag.xpath('./@src').extract_first()
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
