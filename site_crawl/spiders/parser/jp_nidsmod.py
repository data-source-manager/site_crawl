# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class JP_nidsmodParser(BaseParser):
    name = 'jp_nidsmod'
    
    # 站点id
    site_id = "69f5a893-a47a-4763-9004-ce5517de8f92"
    # 站点名
    site_name = "日本防卫研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "69f5a893-a47a-4763-9004-ce5517de8f92", "source_name": "日本防卫研究所", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d9f04-fe6f-11ec-a30b-d4619d029786", "NIDS评论", "http://www.nids.mod.go.jp/publication/commentary/comme_index.html", "政治"),
            ("4a8d9e32-fe6f-11ec-a30b-d4619d029786", "亚太安全研讨会报告", "http://www.nids.mod.go.jp/publication/asia_pacific/index.html", "政治"),
            ("4a8d9f72-fe6f-11ec-a30b-d4619d029786", "国际共同研究", "http://www.nids.mod.go.jp/publication/joint_research/index.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "comme_index" in response.url:
            news_items = response.xpath(
                "//ul[@class='list-pdf']/li")
            if news_items:
                for item in news_items:
                    url = item.xpath(".//div[@class='pdf-links']/a/@href").get()
                    title = item.xpath("./h4/text()").get()
                    Date_str = item.xpath("./text()").get()
                    author_str = item.xpath(".//p[@class='name']/a/text()").get()
                    rsp_url = urljoin(response.url, url)
                    year, mt, day = re.findall("(\d{4})年(\d{1,2})月(\d{1,2})日", Date_str)[0]
                    dt = year + "-" + mt + "-" + day
                    self.Dict[rsp_url] = {"title": title, "dt": dt, "author": author_str}
                    yield rsp_url
        elif "asia_pacific" in response.url:
            news_items = response.xpath(
                "//ul[@class='blet-left mtx']/li")
            if news_items:
                for item in news_items:
                    url = item.xpath("./a/@href").get()
                    title = item.xpath("./text()[2]").get()
                    Date_str = item.xpath("./text()[1]").get()
                    year_str, year_num, mt, day = re.findall("（(.*?)(\d+)年(\d{1,2})月(\d{1,2}).*?）", Date_str)[0]
                    year = self.wareki_year_exchange(year_str, year_num)
                    dt = year + "-" + mt + "-" + day
                    rsp_url = urljoin(response.url, url)
                    self.Dict[rsp_url] = {"title": title, "dt": dt}
                    yield rsp_url
        else:
            news_items = response.xpath(
                "//ul[@class='blet-left mtx']/li")
            if news_items:
                for item in news_items:
                    url = item.xpath("./a/@href").get()
                    title = item.xpath("./text()[1]").get()
                    rsp_url = urljoin(response.url, url)
                    self.Dict[rsp_url] = {"title": title}
                    yield rsp_url

    def get_title(self, response) -> str:
        if self.Dict[response.url]:
            return self.Dict[response.url]['title'].strip()

    def get_author(self, response) -> list:
        authors = []
        if self.Dict[response.url].get("author"):
            authors.append(self.Dict[response.url].get("author"))
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
        return str(result)

    def get_pub_time(self, response) -> str:
        if self.Dict[response.url].get("dt"):
            Date_str = self.Dict[response.url]['dt']
            if Date_str:
                dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
            else:
                return "9999-01-01 00:00:00"
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
            return content
        news_tags = response.xpath(
            "//ul[@class='blet-pdf mtx']/li")
        if news_tags:
            for news_tag in news_tags:
                pdf_src = news_tag.xpath("./a/@href").get()
                if pdf_src:
                    src = urljoin(response.url, pdf_src)
                    file_dic = {
                        "type": "file",
                        "src": src,
                        "name": news_tag.xpath("./a/text()").get() or None,
                        "description": None,
                        "md5src": self.get_md5_value(src) + ".pdf"
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
