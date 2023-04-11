# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from util.time_deal.datetime_helper import fuzzy_parse_datetime
from .base_parser import BaseParser


class MckinseyParser(BaseParser):
    name = 'mckinsey'
    # 站点id
    site_id = "8a3b6385-ed53-4110-94b5-38e780de613e"
    # 站点名
    site_name = "麦肯锡咨询公司"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "8a3b6385-ed53-4110-94b5-38e780de613e", "source_name": "麦肯锡咨询公司", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9a0591c0-2fee-1ef4-d4b1-d9865df6d8c5", "专题", "", "政治"),
            ("91232f86-2f72-11ed-a768-d4619d029786", "专题/亚洲的未来", "https://www.mckinsey.com/featured-insights/future-of-asia/overview", "政治"),
            ("91232f5e-2f72-11ed-a768-d4619d029786", "专题/气候变化", "https://www.mckinsey.com/featured-insights/climate-change", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.pdfDict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="item"]/div[@class="text-wrapper"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="title"]/@content').extract_first()
        if title:
            return title.strip()
        return ""

    def get_author(self, response) -> list:
        author_list = []
        author = response.xpath('//meta[@name="authors-name"]/@content').extract_first()
        if author:
            authors = author.split("|")
            for x in authors:
                if x.strip():
                    author_list.append(x.strip())
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath("//time/text()").extract_first()
        if time_:
            return str(fuzzy_parse_datetime(time_))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        contens = []
        news_tags = response.xpath('//div[@id="divArticleBody"]/article/p|'
                                   '//div[@id="divArticleBody"]/article/section//picture/img|'
                                   '//div[@id="divArticleBody"]/article/section//div[@class="text-wrapper"]//a|'
                                   '//div[@id="divArticleBody"]/article/ul/li|'
                                   '//div[@data-container-id="6266f55bc5a7c"]/p|'
                                   '//div[@class="wrapper universal-page"]/section//div[@class="description"]|'
                                   '//div[@class="wrapper universal-page"]/section//div[@class="description"]/p|'
                                   '//div[@class="wrapper universal-page"]/section//h3')
        if news_tags:
            for new_tag in news_tags:
                if new_tag.root.tag in ["p", "li", "div", "h3"]:
                    contens.extend(self.parse_text(new_tag))
                if new_tag.root.tag == "img":
                    contens.append(self.parse_media(response, new_tag))
                if new_tag.root.tag == "a":
                    contens.append(self.parse_file(response, new_tag))
        return contens

    def get_detected_lang(self, response) -> str:
        return "en"

    def parse_text(self, news_tag) -> list:
        cons = news_tag.xpath('./text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('alt'),
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("./@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath(".//text()").extract_first().strip(),
            "description": None,
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
