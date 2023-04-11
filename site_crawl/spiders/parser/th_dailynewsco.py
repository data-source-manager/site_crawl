# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import requests

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class TH_dailynewscoParser(BaseParser):
    name = 'th_dailynewsco'
    
    # 站点id
    site_id = "da847e53-f868-404f-9bc8-b3367d4596ce"
    # 站点名
    site_name = "泰国每日新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "da847e53-f868-404f-9bc8-b3367d4596ce", "source_name": "泰国每日新闻", "direction": "th", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d0d1e-fe6f-11ec-a30b-d4619d029786", "国际文章", "https://www.dailynews.co.th/article/articles_group/%E0%B8%95%E0%B9%88%E0%B8%B2%E0%B8%87%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B9%80%E0%B8%97%E0%B8%A8/page/3/", "国际"),
            ("4a8d0cba-fe6f-11ec-a30b-d4619d029786", "国际新闻", "https://www.dailynews.co.th/news_group/%e0%b8%95%e0%b9%88%e0%b8%b2%e0%b8%87%e0%b8%9b%e0%b8%a3%e0%b8%b0%e0%b9%80%e0%b8%97%e0%b8%a8/", "国际"),
            ("7ae0dffa-515c-96f1-ba62-ac8614d02437", "政治", "", "政治"),
            ("5a8a23d6-a364-34d4-9c6e-7791c0478884", "政治/专栏作家", "https://www.dailynews.co.th/article/articles_group/%e0%b8%81%e0%b8%b2%e0%b8%a3%e0%b9%80%e0%b8%a1%e0%b8%b7%e0%b8%ad%e0%b8%87/%e0%b8%84%e0%b8%ad%e0%b8%a5%e0%b8%b1%e0%b8%a1%e0%b8%99%e0%b8%b4%e0%b8%aa%e0%b8%95%e0%b9%8c/", "国际"),
            ("2b346cd9-f285-3aec-9713-464a775d1646", "政治/沿着军营", "https://www.dailynews.co.th/article/articles_group/%e0%b8%81%e0%b8%b2%e0%b8%a3%e0%b9%80%e0%b8%a1%e0%b8%b7%e0%b8%ad%e0%b8%87/%e0%b8%84%e0%b8%ad%e0%b8%a5%e0%b8%b1%e0%b8%a1%e0%b8%99%e0%b8%b4%e0%b8%aa%e0%b8%95%e0%b9%8c/", "国际"),
            ("0e910e6f-ee52-4f3f-bf44-37e0387cdeaf", "政治文章", "https://www.dailynews.co.th/article/articles_group/%E0%B8%81%E0%B8%B2%E0%B8%A3%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87/", "政治"),
            ("ae808fb2-5b57-478f-8cec-1c7b1f383d14", "政治新闻", "https://www.dailynews.co.th/news/news_group/politics-news/", "政治"),
            ("4a8d0c88-fe6f-11ec-a30b-d4619d029786", "犯罪", "https://www.dailynews.co.th/news/news_group/%E0%B8%AD%E0%B8%B2%E0%B8%8A%E0%B8%8D%E0%B8%B2%E0%B8%81%E0%B8%A3%E0%B8%A3%E0%B8%A1/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "da847e53-f868-404f-9bc8-b3367d4596ce"
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath(
            "//h1[@class='elementor-post__title']/a|//h3[@class='elementor-post__title']/a")
        if news_items:
            for item in news_items:
                news_url = item.xpath("./@href").get()
                title = item.xpath("./text()").get()
                rsp_url = urljoin(response.url, news_url)
                self.Dict[rsp_url] = title
                yield rsp_url

    def get_title(self, response) -> str:
        title = self.Dict[response.url]
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        auhtor_strs = response.xpath("//p[@class='xg1']/a/text()").get()
        if auhtor_strs:
            authors.append(auhtor_strs)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//meta[@property='article:modified_time']/@content").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[contains(@class,' elementor-widget elementor-widget-theme-post-content') or contains(@class,'elementor-widget-theme-post-featured-image elementor-widget-image')]/div[@class='elementor-widget-container']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "h5", "span", "p", "blockquote"]:
                    if news_tag.xpath(".//img"):
                        img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src", des_xpath=".//img/@alt")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["img", "figure"]:
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src|.//img/@src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        if text_dict:
                            content.append(text_dict)
        file_src = response.xpath("//a[contains(@class,'dk-article__download')]/@href").get()
        if file_src:
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            content.append(file_dic)

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
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        tl_type = response.url.replace("https://www.dailynews.co.th", "")
        rsp_url = f"https://www.dailynews.co.th/api/v1/stats/aggregate?site_id=dailynews.co.th&metrics=visitors,pageviews&filters=event:page=={tl_type}"
        rsp = requests.get(rsp_url)
        if rsp.status_code == 200:
            read_count = rsp.json()['results']['pageviews']['value']
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
