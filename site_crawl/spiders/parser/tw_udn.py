# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.site_deal.interface_helper import facebook_like_count_interface
from util.time_deal import datetime_helper

"""
    模版
"""


class TwUdnParser(BaseParser):
    name = 'udn'
    
    # 站点id
    site_id = "cd5a3b3e-6638-4eef-b078-9453dd06e1e1"
    # 站点名
    site_name = "联合新闻网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "cd5a3b3e-6638-4eef-b078-9453dd06e1e1", "source_name": "联合新闻网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b8dea-fe6f-11ec-a30b-d4619d029786", "两岸", "https://udn.com/news/cate/2/6640", "政治"),
            ("5f385c33-cf88-48c3-a323-f72a5bf482d5", "产经", "https://udn.com/news/cate/2/6644", "政治"),
            ("4a8b8d7c-fe6f-11ec-a30b-d4619d029786", "全球", "https://udn.com/news/cate/2/7225", "政治"),
            ("b0c22502-7218-11ed-a54c-d4619d029786", "即时", "https://udn.com/news/breaknews/1", "政治"),
            ("6cc94af4-97be-4fb3-bf37-11e18bcfacb0", "社会", "https://udn.com/news/cate/2/6640", "政治"),
            ("b0c224a8-7218-11ed-a54c-d4619d029786", "要闻", "https://udn.com/news/cate/2/6638", "政治"),
            ("4a8b9182-fe6f-11ec-a30b-d4619d029786", "评论", "https://udn.com/news/cate/2/6643", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "cd5a3b3e-6638-4eef-b078-9453dd06e1e1"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="story-list__news "]//h3/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                if "7225" not in news_urls:
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1/text()').extract_first(default="")
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
        time_ = response.xpath('//meta[@name="date"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//section[@id="keywords"]/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//section[@class="article-content__editor "]/*|'
                                   '//div[@id="story_body"]/p|//figure|'
                                   '//div[@id="story_body"]/div/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "figcaption"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "figure":
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
        proxy = {
            "https": "http://127.0.0.1:7890",
            "http": "http://127.0.0.1:7890"
        }
        return facebook_like_count_interface(response.url, '//span[@class="_5n6h _2pih"]/text()')

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
