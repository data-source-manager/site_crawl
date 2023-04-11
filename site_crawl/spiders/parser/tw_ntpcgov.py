# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class TW_ntpcgovParser(BaseParser):
    name = 'tw_ntpcgov'
    
    # 站点id
    site_id = "7336ac21-7a4b-4b46-b7e9-90c9f7d80b99"
    # 站点名
    site_name = "新北市政府"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7336ac21-7a4b-4b46-b7e9-90c9f7d80b99", "source_name": "新北市政府", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("af0ee00d-45d4-357f-80d5-67acfc56275c", "市府消息", "", "政治"),
            ("4a8f62bc-fe6f-11ec-a30b-d4619d029786", "市府消息/市政新闻", "https://www.ntpc.gov.tw/ch/home.jsp?id=e8ca970cde5c00e1&qclass=201309160001", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.DICT1 = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@class='list']/div[@class='con']/div//a/@href").extract() or ""
        if news_urls:
            for index, news_url in enumerate(news_urls):
                if not news_url.startswith('http'):
                    news_url = 'https://www.ntpc.gov.tw/ch/' + news_url
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='stitle']/text()").get()
        return title or ""

    def get_author(self, response) -> list:
        author_list = []
        author_s = response.xpath("//*[text()[contains(.,'聯絡人：')]]/following-sibling::node()").get()
        if author_s:
            author_list.append(author_s)
        return author_list

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.xpath("//*[text()[contains(.,'發佈日期：')]]/following-sibling::node()").extract_first() or ""
        dt_ = datetime_helper.fuzzy_parse_timestamp(time_)
        if dt_:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:

        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//li[@class='con']/node()")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag, './@alt')
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dic = self.parse_text(li)
                        if text_dic:
                            content.append(text_dic)
        imgs_node = response.xpath("//div[@class='pic_news']//img")
        for img in imgs_node:
            img_src = img.xpath("./@src").get()
            if img_src:
                img_url = urljoin(response.url, img_src)
                dic = {"type": "image",
                       "name": None,
                       "md5src": self.get_md5_value(img_url) + '.jpg',
                       "description": None,
                       "src": img_url}
                content.append(dic)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if 'Prime Minister of Australia' in x:
                    continue
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, descrption_xpath):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": response.xpath(descrption_xpath).extract_first(),
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag, description_xpath):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": news_tag.xpath(description_xpath).extract_first(),
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url, news_tag.xpath("").extract_first())
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
