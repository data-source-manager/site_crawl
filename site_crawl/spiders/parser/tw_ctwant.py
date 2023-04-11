# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class TwCtwantParser(BaseParser):
    name = 'ctwant'
    
    # 站点id
    site_id = "c8f4cf29-1363-40ff-aeff-37342849aedf"
    # 站点名
    site_name = "CTWANT"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c8f4cf29-1363-40ff-aeff-37342849aedf", "source_name": "CTWANT", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8c688c-fe6f-11ec-a30b-d4619d029786", "国际", "https://www.ctwant.com/category/%E5%9C%8B%E9%9A%9B?page=1", "政治"),
            ("98254e53-420b-4062-920e-18f14704e936", "国际/大陆", "https://www.ctwant.com/category/%E5%9C%8B%E9%9A%9B/%E5%A4%A7%E9%99%B8", "其他"),
            ("ce94c478-66c5-4488-b35f-639c4d98921e", "国际/最新", "https://www.ctwant.com/category/%E5%9C%8B%E9%9A%9B/%E6%9C%80%E6%96%B0", "其他"),
            ("4a8c6828-fe6f-11ec-a30b-d4619d029786", "政治", "https://www.ctwant.com/category/%E6%94%BF%E6%B2%BB?page=1", "政治"),
            ("a58292c9-1ab5-4920-b0de-02930fccdb70", "政治/人物", "https://www.ctwant.com/category/%E6%94%BF%E6%B2%BB/%E4%BA%BA%E7%89%A9", "政治"),
            ("69c51f50-b620-45a2-a4c7-86f6faab9fbe", "政治/焦点", "https://www.ctwant.com/category/%E6%94%BF%E6%B2%BB/%E7%84%A6%E9%BB%9E", "政治"),
            ("a022568f-cba2-43a4-900c-69f5197dda44", "政治/评论", "https://www.ctwant.com/category/%E6%94%BF%E6%B2%BB/%E8%A9%95%E8%AB%96", "政治"),
            ("4a8c6738-fe6f-11ec-a30b-d4619d029786", "社会", "https://www.ctwant.com/category/%E7%A4%BE%E6%9C%83?page=1", "政治"),
            ("4a8c67b0-fe6f-11ec-a30b-d4619d029786", "财经", "https://www.ctwant.com/category/%E8%B2%A1%E7%B6%93?page=1", "政治"),
            ("e2c42622-f101-40e3-a926-eaad3598d992", "财经/人物", "https://www.ctwant.com/category/%E8%B2%A1%E7%B6%93/%E4%BA%BA%E7%89%A9", "经济"),
            ("27e22546-c3a4-42b1-923b-f0fcfb63fcd5", "财经/热线", "https://www.ctwant.com/category/%E8%B2%A1%E7%B6%93/%E7%86%B1%E7%B7%9A", "经济"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "c8f4cf29-1363-40ff-aeff-37342849aedf"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[contains(@class,"m-card")]/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="p-article__title"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//p[@class="p-article-info"]/span/text()').extract_first()
        if authors:
            if "：" in authors:
                authors = authors.split("：")[1]
            if authors.strip():
                author_list.append(authors.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//time/@datetime').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@id="article-tag-top"]/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="p-article__img-box"]/*|'
                                   '//article/div/*')
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
        img = news_tag.xpath('.//@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//@alt').extract()).strip(),
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
