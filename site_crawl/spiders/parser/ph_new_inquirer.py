# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class PH_new_inquirerParser(BaseParser):
    name = 'ph_new_inquirer'
    
    # 站点id
    site_id = "1a83d606-3d4e-4627-b6c1-f7e1faa09860"
    # 站点名
    site_name = "菲律宾每日问讯者报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "1a83d606-3d4e-4627-b6c1-f7e1faa09860", "source_name": "菲律宾每日问讯者报", "direction": "ph", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("61735e41-321e-3c12-b725-df11e454d1c3", "全球国家", "", "政治"),
            ("4a8d5f94-fe6f-11ec-a30b-d4619d029786", "全球国家/中东和非洲", "https://globalnation.inquirer.net/category/world-news/middle-east-africa", "政治"),
            ("4a8d5d28-fe6f-11ec-a30b-d4619d029786", "全球国家/亚太地区", "https://globalnation.inquirer.net/category/world-news/asia-australia", "政治"),
            ("4a8d60b6-fe6f-11ec-a30b-d4619d029786", "全球国家/欧洲", "https://globalnation.inquirer.net/category/world-news/europe", "政治"),
            ("4a8d5e7c-fe6f-11ec-a30b-d4619d029786", "全球国家/每洲", "https://globalnation.inquirer.net/category/world-news/us-canada", "政治"),
            ("3fa4bc7e-13a6-458f-aa0f-4ea753c0dc45", "商业", "https://business.inquirer.net/", "经济"),
            ("7595c7e5-8c02-439a-a2da-d726f7ac592d", "消息", "https://newsinfo.inquirer.net/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@id="ch-ls-head"]/h2/a/@href'
            '|//div[@id="new-channel-left"]//h1/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            news_url = urljoin(response.url, news_url)
            print(news_url)
            if news_url == "https://business.inquirer.net/":
                continue
            yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='entry-title']/text()").get()
        return title or ""

    def get_author(self, response) -> list:
        authors = []
        auhtor_str = response.xpath("//div[@id='art_author']/span/a/text()").get()
        if auhtor_str:
            authors.append(auhtor_str)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//meta[@property='article:published_time']/@content").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@id='article_tags']/span/a/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[@id='article_content']/div/*|//div[@id='article_content']/div//img[not(contains(@src,'svg'))]")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src",
                                             des_xpath="//p[@class='wp-caption-text']/text()")
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
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = news_tag.xpath("./source/@src").extract_first()
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
        return 0

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
