# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class IN_idsaParser(BaseParser):
    '''
    存在评论
    '''
    name = 'in_idsa'
    
    # 站点id
    site_id = "341f7494-08fa-40c6-8f4f-e4c3302885a5"
    # 站点名
    site_name = "印度国防与分析研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "341f7494-08fa-40c6-8f4f-e4c3302885a5", "source_name": "印度国防与分析研究所", "direction": "in", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8dc15a-fe6f-11ec-a30b-d4619d029786", "MP-IDSA新闻", "https://www.idsa.in/idsanews", "政治"),
            ("969ee52c-48f5-4fad-ae6d-296874536657", "专栏和文章", "https://www.idsa.in/idsanews/opeds", "政治"),
            ("4a8dc1b4-fe6f-11ec-a30b-d4619d029786", "新闻文摘", "https://www.idsa.in/newsdigests", "政治"),
            ("e95acd11-13e4-4aa6-8950-d1c1ed4a527c", "评论和简报", "https://www.idsa.in/new", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath(
            "//div[@class='tittle']/a[1]|//div[@class='publication-content']/h2/a")
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
        author_a = response.xpath("//*[text()[contains(.,'Editor')]]/parent::strong/parent::div/text()").get()
        if author_a:
            authors.append(author_a)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//span[@class='date-display-single']/text()").get()
        if Date_str:
            dt_ = datetime.strptime(Date_str.strip(), "%B %d, %Y")
            return datetime_helper.parseTimeWithOutTimeZone(dt_, site_name="印度国防与分析研究所")

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
            "//div[@class='field-item even']/*|//div[@class='aboutdigest-content']/*|//div[@class='aboutdigest-image']/img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "h5", "span", "p", "blockquote"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["img"]:
                    con_img = self.parse_img(response, news_tag, img_xpath="./@data-lazy-src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag == "div" and "gmail_default" in news_tag.root.get("class", "") or \
                        "gmail_quote" in news_tag.root.get("class", ""):
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
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
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url and '.jpg' in img_url:
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
