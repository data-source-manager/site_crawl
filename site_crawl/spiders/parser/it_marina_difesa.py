# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.time_deal.translatetTime import itDict

"""
    模版
"""


class ItMarinaParser(BaseParser):
    name = 'marina'
    
    # 站点id
    site_id = "f7141c2a-19a1-4f6e-b0a3-6c2f6da41ab3"
    # 站点名
    site_name = "marina"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f7141c2a-19a1-4f6e-b0a3-6c2f6da41ab3", "source_name": "marina", "direction": "it", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e700d314-7607-11ed-ad4d-d4619d029786", "新闻", "https://www.marina.difesa.it/media-cultura/Notiziario-online/Pagine/elenco.aspx", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.article_pub = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//ul[@class="list"]/li')
        if news_urls:
            for news_url in news_urls:
                url = "https://www.marina.difesa.it" + news_url.xpath('.//a/@href').extract_first().strip()
                pub_time = news_url.xpath('//span[@class="data"]/text()').extract_first()
                self.article_pub[url] = pub_time.strip()
                yield url

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        if title:
            if "-" in title:
                return title.split("-")[0].strip()
        return ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = self.article_pub[response.url]
        if time_:
            time_list = time_.strip().split(" ")
            time_list[1] = itDict[time_list[1]]
            date_ = datetime.strptime("".join(time_list), "%d %m %Y %H.%M")
            return datetime_helper.parseTimeWithOutTimeZone(date_, site_name="marina")

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="ms-rtestate-field"]/*|'
                                   '//div[@class="slide-image"]|'
                                   '//div[@class="ms-rtestate-field"]/span/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "p", ]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "blockquote":
                    for tag in news_tag.xpath('./p'):
                        con_text = self.parseOnetext(tag)
                        if con_text:
                            content.extend(con_text)
                if news_tag.root.tag == "ul":
                    for tag in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(tag)
                        if con_text:
                            content.extend(con_text)
                if news_tag.root.tag == "div":
                    for img in news_tag.xpath('//div[@class="slide-image"]/div/a'):
                        self.parse_img(response, img)

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
        img = news_tag.xpath('./@href').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
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
