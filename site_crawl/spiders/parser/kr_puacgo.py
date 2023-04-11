# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

import requests
from parsel import Selector

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_puacgoParser(BaseParser):
    name = 'kr_puacgo'
    
    # 站点id
    site_id = "3eda8858-cfb4-404f-67e0-7bc68192f0bd"
    # 站点名
    site_name = "韩国民主和平统一咨询会议"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "3eda8858-cfb4-404f-67e0-7bc68192f0bd", "source_name": "韩国民主和平统一咨询会议", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8dd6ea-fe6f-11ec-a30b-d4619d029786", "公告", "https://www.puac.go.kr/ntcnBbs/list.do?bbsId=NABSMSTR000000000020", "政治"),
            ("4a8dd744-fe6f-11ec-a30b-d4619d029786", "出版物", "https://www.puac.go.kr/pblcteBbs/list.do?bbsId=NABSMSTR000000000008", "政治"),
            ("4a8dd690-fe6f-11ec-a30b-d4619d029786", "新闻稿", "https://www.puac.go.kr/ntcnBbs/list.do?bbsId=NABSMSTR000000000016", "政治"),
            ("4a8dd62c-fe6f-11ec-a30b-d4619d029786", "消息", "https://www.puac.go.kr/ntcnBbs/list.do?bbsId=NABSMSTR000000000017", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}
        self.method = 'post'

    def parse_list(self, response) -> list:
        if "NABSMSTR000000000008" not in response.url:
            bbsId = response.url.split("bbsId=")[-1]
            data = {"pageIndex": 1,
                    "searchCtgry": "",
                    "bbsId": bbsId,
                    "nttId": "",
                    "searchCondition": 1,
                    "searchKeyword": ""}
            html_parser = requests.post("https://www.puac.go.kr/ntcnBbs/subList.do", data=data).text
            res = Selector(html_parser)
            news_ids = res.xpath("//td[@class='subject']/a/@onclick").extract() or []
            titles = res.xpath("//td[@class='subject']/a/text()").getall()
            if news_ids:
                for index, news_id in enumerate(news_ids):
                    id = re.findall("fncBbsDetail\(\'(.*?)\'\);", news_id)[0]
                    url = "https://www.puac.go.kr/ntcnBbs/detail.do?pageIndex=1&searchCtgry=&bbsId={}&nttId={}&searchCondition=1&searchKeyword="
                    post_url = url.format(bbsId, id)
                    self.Dict[post_url] = {"title": titles[index]}
                    yield post_url
        else:
            bbsId = response.url.split("bbsId=")[-1]
            data = {"pageIndex": 1,
                    "searchCtgry": "",
                    "bbsId": bbsId,
                    "nttId": "",
                    "searchCondition": 1,
                    "searchKeyword": ""}
            html_parser = requests.post("https://www.puac.go.kr/ntcnBbs/subList.do", data=data).text
            res = Selector(html_parser)
            news_ids = res.xpath("//dd[@class='down']/button[@class='pdf_down']/@onclick").extract() or []
            titles = res.xpath("//dd[@class='subject']/text()[normalize-space()]").getall()
            times = res.xpath("//span[@class='date']/text()").getall()
            if news_ids:
                for index, news_id in enumerate(news_ids):
                    id = re.findall("fncAtchFlDown\(\'(.*?)\'\);", news_id)[0]
                    url = "https://www.puac.go.kr/cmm/atchFlDown.do?atchFileId={}"
                    get_url = url.format(id)
                    self.Dict[get_url] = {"title": titles[index], 'dt': times[index]}
                    yield get_url

    def get_title(self, response) -> str:
        title = self.Dict[response.url]['title']
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        if "atchFileId" in response.url:
            return authors
        author_a = response.xpath("//*[text()[contains(.,'작성자 :')]]/span/text()").get()
        if author_a:
            authors.append(author_a)
        return authors

    def get_pub_time(self, response) -> str:
        if "atchFileId" not in response.url:
            Date_str = response.xpath("//*[text()[contains(.,'작성일 :')]]/span/text()").get()
        else:
            Date_str = self.Dict[response.url]['dt']
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        if "atchFileId" in response.url:
            pdf_src = response.url
            file_dic = {
                "type": "file",
                "src": pdf_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(pdf_src) + ".pdf"
            }
            content.append(file_dic)
            return content
        news_tags = response.xpath("//div[@class='contentHtml']/node()")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'center', 'div']:
                    if news_tag.xpath("./img"):
                        img_src = self.parse_img(response, news_tag, img_xpath="./img/@src")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag == 'img':
                    img_src = self.parse_img(response, news_tag, img_xpath="./@src")
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
        if img_url and "scorecardresearch" not in img_url:
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
        if "atchFileId" in response.url:
            return read_count
        read_count_str = response.xpath("//*[text()[contains(.,'조회 :')]]/span/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
