# -*- coding: utf-8 -*-
import re
from datetime import timedelta, datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class KoreaParser(BaseParser):
    name = 'korea'
    
    # 站点id
    site_id = "90bebc39-0b79-4eeb-abd9-798cfabac3ed"
    # 站点名
    site_name = "韩国政府网站"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "90bebc39-0b79-4eeb-abd9-798cfabac3ed", "source_name": "韩国政府网站", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91230204-2f72-11ed-a768-d4619d029786", "新闻焦点", "https://www.korea.net/NewsFocus/policies", "政治"),
            ("9123057e-2f72-11ed-a768-d4619d029786", "新闻稿", "https://www.korea.net/Government/Briefing-Room/Press-Releases", "政治"),
            ("f75f804f-5575-39c9-999b-2fc2302048be", "问题焦点", "", "政治"),
            ("9123031c-2f72-11ed-a768-d4619d029786", "问题焦点/国家事务", "https://www.korea.net/Government/Current-Affairs/National-Affairs", "政治"),
            ("91230452-2f72-11ed-a768-d4619d029786", "问题焦点/外交事务", "https://www.korea.net/Government/Current-Affairs/Foreign-Affairs", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="list-box"]/a/@href').extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                formatstr = re.findall("View[\s\S]+", news_url)[0].replace("View(", "").replace(")", "").split(",")
                if "Affairs" in response.url:
                    news_url = "https://www.korea.net/{0}?affairId={1}".format(formatstr[0], formatstr[1])
                if "Press-Releas" in response.url:
                    news_url = "https://www.korea.net/{0}view?articleId={1}&type={3}&insttCode={4}&{2}".format(
                        formatstr[0],
                        formatstr[1],
                        formatstr[3],
                        formatstr[4],
                        formatstr[2])
                if "policies" in response.url:
                    news_url = "https://www.korea.net/{0}/view?articleId={1}&{2}".format(formatstr[0], formatstr[1],
                                                                                         formatstr[2])

                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//h2[@id="print_title"]/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        if "policies" in response.url or "Press-Releases" in response.url:
            pub = response.xpath('//p[@class="date"]/text()').extract_first()
            if pub:
                pub = str(
                    datetime.strptime(pub.replace("T", " ").split("+")[0], "%Y-%m-%d %H:%M:%S") + timedelta(hours=-2))
            return pub
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        if "policies" in response.url:
            tags = response.xpath('//meta[@name="keywords"]/@content').extract_first().split(",")
            if tags:
                return tags
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 提升作用域
        news_tags = response.xpath("")
        if "Affairs" in response.url:
            news_tags = response.xpath('//div[@class="box-gray"]/p')
        if "policies" in response.url or "Press-Releases" in response.url:
            news_tags = response.xpath(
                '//div[@id="content_text_ALLBOX"]/p|//div[@id="content_text_ALLBOX"]/div|//div[@class="atta-file-wrap"]/ul/li')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "div":
                    img = self.parse_img(response, news_tag)
                    content.append(img)
                if news_tag.root.tag == "li":
                    content.append(self.parse_file(response, news_tag))
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict.get("data"):
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "en"

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

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": response.xpath(".//p/text()").extract_first(),
               "src": img_url
               }
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath(".//a/text()").extract_first(),
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
