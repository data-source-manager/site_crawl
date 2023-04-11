# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Ru_govermentParser(BaseParser):
    name = 'ru_goverment'
    
    # 站点id
    site_id = "2e67e869-b1ac-4e2e-912f-6f0650336e92"
    # 站点名
    site_name = "俄罗斯政府"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "2e67e869-b1ac-4e2e-912f-6f0650336e92", "source_name": "俄罗斯政府", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91230ed4-2f72-11ed-a768-d4619d029786", "政府会议", "http://government.ru/meetings/", "政治"),
            ("91230f38-2f72-11ed-a768-d4619d029786", "文件", "http://government.ru/docs/", "政治"),
            ("91230e66-2f72-11ed-a768-d4619d029786", "消息", "http://government.ru/news/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//a[@class='headline__link open-reader-js']/@href").extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h3[@class='reader_article_headline']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = response.xpath(
            '//div[contains(@class,"reader_article_meta_person")]//li/a/text()').extract()
        author = []
        if authors:
            author.extend(authors)
        return author

    def get_pub_time(self, response) -> str:
        id = response.url.split("/")[-2]
        time_ = response.xpath('//div[@data-id="{}"]//time/@datetime'.format(id)).extract_first() or ""
        dt_ = datetime_helper.fuzzy_parse_timestamp(time_)
        if dt_:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath(
            '//div[@class="reader_article_meta reader_article_meta_top"]//li[@class="reader_article_tags_item"]/a/text()').extract() or ""
        return [tags.strip() for tags in tags_node]

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[contains(@class,'reader_article_body')]/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                elif news_tag.root.tag == 'div' and "reader_article_box_video_container" in news_tag.root.get("class",
                                                                                                              ""):
                    video_dict = self.parse_media(response, news_tag, xpath_src=".//video/@src",
                                                  xpath_des=".//p[@class='figure_caption_title']/text()")
                    content.append(video_dict)
                elif news_tag.root.tag == 'div' and "reader_article_doc" in news_tag.root.get("class", ""):
                    file_dict = self.parse_file(response, news_tag)
                    content.append(file_dict)
                elif news_tag.root.tag == 'div' and "reader_article_box" in news_tag.root.get("class", ""):
                    img_dict = self.parse_img(response, news_tag, xpath_src=".//img[@class='figure_img']/@src",
                                              xpath_des=".//img[@class='figure_img']/@alt")
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", "li"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
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
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, xpath_src='', xpath_des=''):
        img_url = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
        if img_url:
            if img_url:
                dic = {"type": "image",
                       "name": None,
                       "md5src": self.get_md5_value(img_url) + '.jpg',
                       "description": news_tag.xpath(xpath_des).extract_first() if xpath_des else None,
                       "src": img_url}
                return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("//a[@class='entry_file_link']/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath("//h2[@class='aside_h2']/text()").extract_first(),
            "description": news_tag.xpath("//h3[@class='entry_title entry_title__file']/text()").extract_first(),
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag, xpath_src='', xpath_des=''):
        video_src = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
        if video_src:
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": news_tag.xpath(xpath_des).extract_first() if xpath_des else None,
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
