# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_korvaorParser(BaseParser):
    name = 'kr_korvaor'
    
    # 站点id
    site_id = "654b177d-9a02-479e-92d1-9f237a86cb4b"
    # 站点名
    site_name = "退伍军人协会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "654b177d-9a02-479e-92d1-9f237a86cb4b", "source_name": "退伍军人协会", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91232dd8-2f72-11ed-a768-d4619d029786", "各级新闻", "https://www.korva.or.kr/sub0601_bbs.asp?tbName=all", "政治"),
            ("91232da6-2f72-11ed-a768-d4619d029786", "新闻发布室", "https://www.korva.or.kr/board_list.asp?tables=k_b_lifenews", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//td[@class='title']//a/@href").extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//td[@class='t_left']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        if not news_issue_title:
            news_issue_title = response.xpath('//meta[@property="og:description"]/@content').extract_first(
                default="").strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath("//*[text()[contains(.,'등록일')]]/following-sibling::td[1]/text()").extract_first() or ""
        if time_:
            return str(datetime_helper.fuzzy_parse_datetime(time_))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath("//ul[@class='td-tags td-post-small-box clearfix']/li//text()")
        return [tags.strip() for tags in tags_node]

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='bd_view']//tr/td[@colspan='6']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == 'img':
                    img_dict = self.parse_img(response, news_tag)
                    if img_dict:
                        content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    if news_tag.xpath(".//a[contains(@href,'pdf')]/@href"):
                        file_dict = self.parse_file(response, news_tag)
                        content.append(file_dict)
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
                    new_cons.append(x.replace("&nbsp", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//a[contains(@href,'pdf')]/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": news_tag.xpath(".//a[contains(@href,'pdf')]/text()").extract_first(),
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
        read_count = 0
        read_count_str = response.xpath(
            "//*[text()[contains(.,'조회수')]]/following-sibling::td[1]/text()").extract_first()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
