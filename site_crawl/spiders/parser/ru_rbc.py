# -*- coding: utf-8 -*-
"""
@fix: liyun - 2023-01-07: 修正正文字段分散问题，合并同一个<p>|<div>中的文本字段
"""
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class RU_rbcParser(BaseParser):
    name = 'ru_rbc'
    
    # 站点id
    site_id = "46add5c6-2bdb-43aa-b020-4f529d97df71"
    # 站点名
    site_name = "RBC"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "46add5c6-2bdb-43aa-b020-4f529d97df71", "source_name": "RBC", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9123520e-2f72-11ed-a768-d4619d029786", "国家项目", "https://www.rbc.ru/national", "政治"),
            ("91235240-2f72-11ed-a768-d4619d029786", "政治", "https://www.rbc.ru/politics/?utm_source=topline", "政治"),
            ("91235268-2f72-11ed-a768-d4619d029786", "经济", "https://www.rbc.ru/economics/?utm_source=topline", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//div[@class='item__wrap l-col-center']/a[@class='item__link']/@href").extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[contains(@class,'article__header__title-in')]/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        author_str = response.xpath("//span[@class='article__authors__author__name']/text()").get()
        if author_str:
            author_list.append(author_str.strip())
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = response.xpath("//time[@class='article__header__date']/@datetime").get()
        if datePublished_str:
            dt_ = datetime_helper.fuzzy_parse_timestamp(datePublished_str)
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt_))
            return str(dt)
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags_node = response.xpath(
            "//div[@class='article__tags__container']/a[@class='article__tags__item']/text()").getall()
        if tags_node:
            tags_list.extend(tags_node)
        return tags_list

    """
    @fix: liyun - 2023-01-07: 修正正文字段分散问题，合并同一个<p>|<div>中的文本字段
    """

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@itemprop='articleBody']/*"
                                   "|//div[@itemprop='articleBody']/div[@class='article__picture__wrap']//img"
                                   "|//div[@itemprop='articleBody']//div[@class='textonline__content__text']/*"
                                   "|//div[@class='article__text article__text_free']//img")
        if news_tags:
            for news_tag in news_tags:
                # 合并<p>&<div>标签中的文本字段
                if news_tag.root.tag == "p" or (
                        news_tag.root.tag == "div" and "article__" in news_tag.root.get("class", "")):
                    texts = {
                        "data": " ".join([t.get("data") for t in self.parse_text(news_tag)]),
                        "type": "text"
                    }
                    texts.get("data") and content.append(texts)

                elif news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
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

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip() and ".css-" not in x:
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@src').extract_first()

        if img and ".html" not in img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath('./@alt').extract_first(),
                   "src": img}
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
