# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Usa_ang_afmilParser(BaseParser):
    name = 'usa_ang_afmil'
    
    # 站点id
    site_id = "a6d44b01-2961-405c-8deb-2680f7092545"
    # 站点名
    site_name = "美国空军国民警卫队"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "a6d44b01-2961-405c-8deb-2680f7092545", "source_name": "美国空军国民警卫队", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("912322f2-2f72-11ed-a768-d4619d029786", "消息", "https://www.ang.af.mil/News/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@class='summary']/h1/a/@href").extract() or ""
        if news_urls:
            for news_url in (news_urls):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//header/h1/text()").extract_first() or ""
        return title

    def get_author(self, response) -> list:
        author = []
        authors = response.xpath(
            "//div[@class='meta']//*[text()[contains(.,'By')]]/text()").extract_first()
        if authors:
            for author_a in authors.split(","):
                author.append(author_a.replace("By", "").replace("Video by", "").strip())
        return author

    def get_pub_time(self, response) -> str:
        time_str = response.xpath("//time/@datetime").extract_first() or ""
        dt = time_str.replace("|", "")
        dt_ = datetime_helper.fuzzy_parse_timestamp(dt)
        if dt_:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath(
            "//a[@class='article-detail-tag']/text()").extract()
        tags = [tags.strip() for tags in tags_node]
        return tags

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//section[@class='article-detail-content']/node()|//section[@class='article-detail-content']/p/node()|//ul[@class='slides']/li[@class='slide']//a[@class='fancybox-item']")

        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_data = news_tag.root.replace("\r\n", "").strip()
                        if text_data:
                            text_dict = {"data": text_data, "type": "text"}
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag == 'div' and 'media-inline-medium' in news_tag.root.get("class", ''):
                    img_dict = self.parse_img(response, news_tag, xpath_src=".//img/@src",
                                              xpath_des=".//figcaption[@class='wip-fb-caption']/p/text()")
                    content.append(img_dict)
                elif news_tag.root.tag == "a":
                    img_dict = self.parse_img(response, news_tag, xpath_src="./self::a[contains(@href,'JPG')]/@href",
                                              xpath_des=".//figcaption/p/text()")
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "span"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "div" and "ast-pullquote pullquoteCenter" in news_tag.root.get("class", ""):
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
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, xpath_src='', xpath_des=''):
        if xpath_src:
            img_url = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(xpath_des).extract_first() if xpath_des else None,
                   "src": img_url}
            return dic

    def parse_file(self, response):
        file_src = response.url
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag, xpath_src='', xpath_des=''):
        video_src = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": news_tag.xpath(xpath_des).extract_first(),
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
