# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class DE_auswaertigesParser(BaseParser):
    name = 'de_auswaertiges_amt'
    
    # 站点id
    site_id = "8e33d6d3-4411-48ab-a5b6-5c3235f6ff9b"
    # 站点名
    site_name = "德国外交部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "8e33d6d3-4411-48ab-a5b6-5c3235f6ff9b", "source_name": "德国外交部", "direction": "de", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9952d4f2-a291-3e6e-a31a-0ff4333f12a4", "新闻", "", "政治"),
            ("91236960-2f72-11ed-a768-d4619d029786", "新闻/编辑室", "https://www.auswaertiges-amt.de/de/newsroom/news", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//section[@class='u-section  isnt-margintop ']//div[@class='u-grid-row']//a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='heading__title']/span[@class='heading__title-text']/text()").extract_first(
            default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = response.xpath("//span[@class='heading__meta']/text()[normalize-space()]").get()
        if datePublished_str:
            day, month, yr = datePublished_str.replace("- Artikel", "").strip().split(".")
            dd = yr + "-" + month + "-" + day
            dt = datetime_helper.fuzzy_parse_timestamp(dd)
            Date_mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt))
            return str(Date_mt)
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@class='c-rte--default']/div/*|//div[@class='c-rte--default']/div//picture|//p[@class='quote__paragraph']|//div[@class='figure__wrapper-scroll']//picture")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "picture":
                    con_img = self.parse_img(response, news_tag, img_xpath="./source/@srcset", img_des="./img/@title")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        """"
            可以对一个标签下存在多个段落进行解析
        """
        dic = {}
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'

        return dic

    def parse_img(self, response, news_tag, img_xpath='', img_des=''):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath(img_xpath).extract_first()
        img_src = img.split(",")[-1].strip().split(" ")[0]
        if img_src:
            img_url = urljoin("https://www.auswaertiges-amt.de", img_src)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(img_des).extract_first(),
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath(".//a[contains(@href,'.pdf')]/@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath(".//iframe/@src").extract_first()
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
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
