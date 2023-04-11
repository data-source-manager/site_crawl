# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class JP_kanteigoParser(BaseParser):
    name = 'jp_kanteigo'
    
    # 站点id
    site_id = "0fc035b5-329c-59af-702e-fe8aa00f2da2"
    # 站点名
    site_name = "日本首相官邸"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "0fc035b5-329c-59af-702e-fe8aa00f2da2", "source_name": "日本首相官邸", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8dfd50-fe6f-11ec-a30b-d4619d029786", "内阁记者会", "https://www.kantei.go.jp/jp/tyoukanpress/index.html", "政治"),
            ("4a8dfc6a-fe6f-11ec-a30b-d4619d029786", "新着情报一览", "https://www.kantei.go.jp/jp/news/index.html", "政治"),
            ("4a8dfdbe-fe6f-11ec-a30b-d4619d029786", "首相指示", "https://www.kantei.go.jp/jp/101_kishida/discourse/index.html", "政治"),
            ("4a8dfce2-fe6f-11ec-a30b-d4619d029786", "首相讲话", "https://www.kantei.go.jp/jp/101_kishida/statement/index.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "news" in response.url:
            news_urls = response.xpath("//div[@class='news-list-title']/a")
            if news_urls:
                for news_url in news_urls:
                    rsp_url = news_url.xpath("./@href").get()
                    rsp_title = news_url.xpath('./text()').get()
                    url = urljoin(response.url, rsp_url)
                    self.Dict[url] = {'title': rsp_title}
                    yield url
        else:
            news_urls = response.xpath(
                "//div[@class='news-list-title']/a/@href|//ul[@class='bullet-list']/li/a/@href").extract() or []
            if news_urls:
                for news_url in news_urls:
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if ".pdf" in response.url:
            title = self.Dict[response.url]['title']
            return title.strip() if title else ""
        else:
            title = response.xpath("//h1/text()").extract_first(default="") or ""
            news_issue_title = title.strip()
            return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        if ".pdf" in response.url:
            return []
        else:
            author_a = response.xpath("//div[@class='writen-by']/text()").get()
            if author_a:
                authors.append(author_a.replace("Written By:", "").strip())
            return authors

    def wareki_year_exchange(self, year_str, year_num):
        try:
            value_gengou = year_str
            value_year = int(year_num)
            if value_gengou == '明治' and value_year < 46:
                result = value_year + 1867
            elif value_gengou == '大正' and value_year < 16:
                result = value_year + 1911
            elif value_gengou == '昭和' and value_year < 65:
                result = value_year + 1925
            elif value_gengou == '平成' and value_year < 32:
                result = value_year + 1988
            elif value_gengou == '令和':
                result = value_year + 2018
            else:
                result = None
        except ValueError:
            result = None
        return result

    def get_pub_time(self, response) -> str:
        if ".pdf" in response.url:
            return "9999-01-01 00:00:00"
        else:
            Date_str = response.xpath("//span[@class='date']/text()").get()
            if Date_str:
                time_ = Date_str.replace("更新日：", "")
                mot, dy = re.findall("(\d{1,2})月(\d{1,2})日", time_)[0]
                year_num = re.findall("\d+", time_)[0]
                year = str(self.wareki_year_exchange(time_[:2], year_num))
                dt = year + "-" + mot + "-" + dy
                dt = datetime_helper.fuzzy_parse_timestamp(dt)
                return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
            else:
                return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        if ".pdf" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
        else:
            news_tags = response.xpath("//p|//div[@class='slide-img']/img")
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'div']:
                        text_dict = self.parse_text(news_tag)
                        if text_dict:
                            content.append(text_dict)
                    elif news_tag.root.tag in ["ul", "ol"]:
                        traversal_node = news_tag.xpath("./li")
                        for li in traversal_node:
                            text_dict = self.parse_text(li)
                            content.append(text_dict)
                    elif news_tag.root.tag == 'img':
                        img_src = self.parse_img(response, news_tag, img_xpath="./@src", des_xpath="./@alt")
                        if img_src:
                            content.append(img_src)

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
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
