# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KH_cdriorgParser(BaseParser):
    name = 'kh_cdriorg'
    
    # 站点id
    site_id = "cad219c7-d8a3-40be-ab72-3dc682968f2f"
    # 站点名
    site_name = "柬埔寨发展资源研究院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "cad219c7-d8a3-40be-ab72-3dc682968f2f", "source_name": "柬埔寨发展资源研究院", "direction": "kh", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("92f7d87c-efa6-3c49-9a7b-8026f5d01558", "出版物", "", "政治"),
            ("4a8cebcc-fe6f-11ec-a30b-d4619d029786", "出版物/国际", "http://cdri.org.kh/publication/type/international-publications", "政治"),
            ("4a8cea78-fe6f-11ec-a30b-d4619d029786", "出版物/工作文件", "http://cdri.org.kh/publication/type/working-paper", "政治"),
            ("4a8ceb2c-fe6f-11ec-a30b-d4619d029786", "出版物/柬埔寨的发展评论", "http://cdri.org.kh/publication/type/cambodia-development-review", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath(
            "//h3/a[@class='f22 f-clor-default']|//h2[@class='title']/a[@class='post-url post-title']")
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
            "//div[@class='blog-text']//span[@class='badge badge-info pub-author']/text()").getall()
        if auhtor_strs:
            for author_a in auhtor_strs:
                authors.append(author_a.strip())
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//*[text()[contains(.,' Published: ')]]/following-sibling::b[1]/text()").get()
        if Date_str:
            dt_ = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//*[text()[contains(.,' Keyword: ')]]/following-sibling::node()[1]").get()
        if tags:
            for tag in tags.split(", "):
                tags_list.append(tag.strip())
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[contains(@class,'blog-text')]/node()")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
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
        file_srcs = response.xpath("//a[contains(@id,'pdf')]/@href").getall()
        if file_srcs:
            for file_src in file_srcs:
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
        read_count_str = response.xpath("//span[contains(@class,'views post-meta-views')]/text()").get()
        if read_count_str:
            read_count = int(read_count_str.replace(",", ""))
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
