# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class VN_vietnamplus(BaseParser):
    name = 'vn_vietnamplus'
    
    # 站点id
    site_id = "80340a0e-fc20-8e3d-625c-9d09dc912d77"
    # 站点名
    site_name = "越南通讯社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "80340a0e-fc20-8e3d-625c-9d09dc912d77", "source_name": "越南通讯社", "direction": "vn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8ddb04-fe6f-11ec-a30b-d4619d029786", "国际", "https://zh.vietnamplus.vn/world.vnp", "政治"),
            ("4a8dda8c-fe6f-11ec-a30b-d4619d029786", "时政", "https://zh.vietnamplus.vn/politics/page1.vnp", "政治"),
            ("4a8ddb86-fe6f-11ec-a30b-d4619d029786", "经济", "https://zh.vietnamplus.vn/business.vnp", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//h1/a/@href|//article[@class='story']//h2/a/@href|"
                                   "//article[@class='story story--split']//h2/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='details__headline cms-title']/text()|"
                               "//h1[@class='entry-title']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='source']/time/@datetime").get()

        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@class='tags']/a/text()").getall()
        if tags:
            for tag in tags:
                tags_list.append(tag.strip())
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[contains(@class,'article-body')]//div[contains(@class,'ExternalClass')]/node()|"
            "//div[@class='article-photo']//img|//iframe[@class='cms-video']|//div[@class='entry-content']/*"
            "//div[@class='content article-body cms-body AdAsia']|//div[@class='site-main']/div[2]/div[1]/div[2]|"
            "//div[@class='entry-content']/figure/img")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'center', "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag == "iframe":
                    con_file = self.parse_media(response, news_tag, media_type="mp4")
                    if con_file:
                        content.append(con_file)
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

    def parse_media(self, response, news_tag, media_type):
        videoUrl = news_tag.xpath("./@src").extract_first()
        suffix = f".{media_type}"

        video_dic = {}

        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }

            if suffix == ".mp3":
                video_dic["type"] = "audio"
            elif suffix == ".mp4":
                video_dic["type"] = "video"

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
        if self.Dict.get(response.url):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        repost_source_str = response.xpath("//span[@class='cms-author']/text()").get()
        if repost_source_str:
            self.Dict[response.url] = repost_source_str
            repost_source = repost_source_str
        return repost_source
