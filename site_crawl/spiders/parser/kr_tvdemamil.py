# -*- coding: utf-8 -*-
import re
from datetime import datetime
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_tvdemamilParser(BaseParser):
    name = 'kr_tvdemamil'
    
    # 站点id
    site_id = "7c3885f3-8963-482a-bee4-b20c096ca3d4"
    # 站点名
    site_name = "国防新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7c3885f3-8963-482a-bee4-b20c096ca3d4", "source_name": "国防新闻", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("98ab1242-213d-4d9d-bc8e-b26ddf304ae2", "国防TV", "https://tv.dema.mil.kr/web/home/defencenews", "政治"),
            ("1bd13597-aa91-4605-9905-4baf3c13f92a", "防御焦点", "https://tv.dema.mil.kr/web/home/discussion/mov/homeMovieList.do?menu_seq=1210&pseq=0", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "discussion" in response.url:
            response.meta['method'] = 'post'
            post_ids = response.xpath("//div[@class='relistennig_list']//ul/li//a/@onclick").getall() or []
            if post_ids:
                for post_id in post_ids:
                    post_url_template = 'https://tv.dema.mil.kr/web/home/discussion/mov/homeMovieView.do?'
                    media_seq = re.findall("fn_view\(\'(.*?)\'\)", post_id)[0]
                    postdata = f"media_seq={media_seq}&page_index=1&menu_seq=1210&search_type=TITLE&search_word=&input_pageno="
                    post_url = post_url_template + postdata
                    yield post_url
        news_urls = response.xpath("//ul[@class='defence_clip_list']/li/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//meta[@name='title']/@content").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        # 2023.01.20
        Date_str = response.xpath("//p[@class='date']/text()").get()
        if Date_str:
            time_ = Date_str.replace("등록일자:", "").replace("방송일자:", "")
            dt = datetime.strptime(time_.strip(), "%Y.%m.%d")
            return datetime_helper.parseTimeWithOutTimeZone(dt, site_name="国防新闻")
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='play_cont']/dl/dd/p/node()|//div[@class='play_cont']/dl/dd/strong")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
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
        read_count_str = response.xpath("//*[text()[contains(.,'조회수 :')]]/text()").get()
        if read_count_str:
            read_count = int(read_count_str.replace("조회수 :", ""))
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
