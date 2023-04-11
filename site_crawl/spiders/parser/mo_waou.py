# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class MO_waouParser(BaseParser):
    name = 'mo_waou'
    
    # 站点id
    site_id = "17495ca6-daf8-49f9-adbc-fdd4ba2a95d4"
    # 站点名
    site_name = "新华澳报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "17495ca6-daf8-49f9-adbc-fdd4ba2a95d4", "source_name": "新华澳报", "direction": "mo", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8cf2c0-fe6f-11ec-a30b-d4619d029786", "两岸观察", "https://www.waou.com.mo/category/see/", "政治"),
            ("4a8cf356-fe6f-11ec-a30b-d4619d029786", "中华大地", "https://www.waou.com.mo/category/land/", "政治"),
            ("4a8cf28e-fe6f-11ec-a30b-d4619d029786", "华澳人语", "https://www.waou.com.mo/category/hua/", "政治"),
            ("4a8cf2f2-fe6f-11ec-a30b-d4619d029786", "本澳新闻", "https://www.waou.com.mo/category/news/", "政治"),
            ("4a8cf324-fe6f-11ec-a30b-d4619d029786", "海峡两岸", "https://www.waou.com.mo/category/strait/", "政治"),
            ("4a8cf388-fe6f-11ec-a30b-d4619d029786", "海峡桥", "https://www.waou.com.mo/category/bridge/", "政治"),
            ("462e9f27-cafa-475b-ba8e-09e3011045b3", "百家台", "https://www.waou.com.mo/category/hot/", "政治"),
            ("4a8cf3ba-fe6f-11ec-a30b-d4619d029786", "要闻", "https://www.waou.com.mo/category/hot/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath(
            "//header[contains(@class,'entry-header')]//h2/a")
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
        auhtor_strs = response.xpath(
            "//div[contains(@class,'entry-content')]/p[last()][contains(.,'／文')]/text()").get()
        if auhtor_strs:
            authors.append(auhtor_strs.replace("（", "").replace("）", "").replace("／文", "").strip())
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='date created-date']/a/text()").get()
        if Date_str:

            dt = Date_str.replace("年", "-").replace("月", "-").replace("日", "")
            dt_ = datetime_helper.fuzzy_parse_timestamp(dt)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//a[@class='internalLink']/span/text()").getall()
        if tags:
            tags = list(set(tags))
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[contains(@class,'entry-content')]/p/node()")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root.strip(), "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h4", "h5", "span", "p", "blockquote"]:
                    if news_tag.xpath(".//img"):
                        img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src", des_xpath=".//img/@alt")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["img", "figure"]:
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src|.//img/@src",
                                             des_xpath=".//figcaption[@class='wp-caption-text']/text()")
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
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
