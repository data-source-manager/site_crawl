# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from lxml import etree

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Kr_kima_reParser(BaseParser):
    name = 'kr_kima_re'
    
    # 站点id
    site_id = "c392932d-66d6-4b41-bdd4-9bd2c7528cb5"
    # 站点名
    site_name = "韩国军事研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c392932d-66d6-4b41-bdd4-9bd2c7528cb5", "source_name": "韩国军事研究所", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91232d74-2f72-11ed-a768-d4619d029786", "KIMA媒体", "https://www.kima.re.kr/3.html?Table=ins_bbs28&s=14", "政治"),
            ("91232d10-2f72-11ed-a768-d4619d029786", "KIMA通讯", "https://www.kima.re.kr/5.html?Table=ins_bbs1&s=1", "政治"),
            ("91232cde-2f72-11ed-a768-d4619d029786", "新闻", "https://www.kima.re.kr/5.html?Table=ins_bbs1&s=1", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//tr[contains(@class,'pc')]//td[@class='td_title']/a/@href|//td[@class='text-left']/a/@href|//td[@class='bbs_media_title']/a/@href").extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                if "http" not in news_url:
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//thead/tr/td/text()").extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        author = []
        author_a = response.xpath("//td[@class='writer']/text()[normalize-space()]").extract_first()
        if author_a:
            author.append(author_a.replace("&nbsp", "").strip())
        return author

    def get_pub_time(self, response) -> str:
        pub = response.xpath("//td[@class='date']/text()").extract_first().replace("&nbsp", "").strip()
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
            pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
            return pub_time
        else:
            if "ins_bbs28" in response.url:
                pub_str = response.xpath("//thead/tr/td/text()").extract_first()
                pub = re.findall(".*?\((.*?)\)", pub_str.strip())[0]
                pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
                pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
                return pub_time
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        pass

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//td[@class='bbs-text']/*|//div[@class='bbs_image_view_contents']/iframe")
        file_xpath = response.xpath("//td[@class='file']/a")
        for file_node in file_xpath:
            file_dict = self.parse_file(response, file_node)
            if file_dict:
                content.append(file_dict)

        img_node = response.xpath("//td[@class='file']/center//img")
        img_dict = self.parse_img(response, img_node)
        if img_dict:
            content.append(img_dict)
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in "iframe":
                    video_dict = self.parse_media(response, news_tag)
                    if video_dict:
                        content.append(video_dict)
                elif news_tag.root.tag in "table":
                    html_str = etree.tostring(news_tag.root, encoding="utf-8").decode("utf-8")
                    content.append({'data': html_str, 'type': 'text'})
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
        if news_tag.attrib.get('src'):
            img_url = urljoin(response.url, news_tag.attrib.get('src'))
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": None,
                   "src": img_url
                   }
            return dic

    def parse_file(self, response, news_tag):
        file_hf = news_tag.xpath("./self::a[contains(@href,'pdf')]/@href").extract_first()
        if file_hf:
            file_src = urljoin(response.url, file_hf)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.xpath("./text()").extract_first(),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url, news_tag.xpath("./@src").extract_first())
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
