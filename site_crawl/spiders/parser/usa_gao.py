# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class USA_gaoParser(BaseParser):
    name = 'gao'
    
    # 站点id
    site_id = "9bf27a4d-9cf9-42d9-89c2-7fa5e4b06772"
    # 站点名
    site_name = "政府问责局报告"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "9bf27a4d-9cf9-42d9-89c2-7fa5e4b06772", "source_name": "政府问责局报告", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("912300e2-2f72-11ed-a768-d4619d029786", "报告和证词", "https://www.gao.gov/reports-testimonies", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.DICT1 = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="c-search-result"]/div')
        if news_urls:
            for news_url in news_urls:
                url = urljoin(response.url, news_url.xpath("./h4/a/@href").extract_first())
                pub = news_url.xpath("./div//time[@class='datetime'][1]/text()").extract_first()
                self.DICT1[url] = pub
                yield url

    def get_title(self, response) -> str:
        titles = response.xpath('//meta[@name="twitter:title"]/@content').extract() or ""
        return "".join(titles).replace("\n", "").strip()

    def get_author(self, response) -> list:
        pass

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        pub = self.DICT1[response.url]
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath(
            "//div[@class='views-row']//div[@class='field-content']/a/text()| "
            "//div[@class='views-row']//div[@class='field-content']/span/text()").extract()
        return [tags.strip() for tags in tags_node]

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@class='field__item']/*|//div[@class='field__item']/p/img|"
            "//div[@class='view--recommendations--inner']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag, './@alt')
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", "li"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == 'div' and "views-element-container" in news_tag.root.get("class", ""):
                    dic = {}
                    html_str = news_tag.xpath("./table")
                    dic['data'] = html_str
                    dic['type'] = 'text'
                    content.append(dic)

        file_fields = response.xpath("//div[@class='field-group-content-wrapper']//div[@class='field__item']")
        for file_node in file_fields:
            file_pdf = self.parse_file(response, file_node,
                                       ".//div[contains(@class,'field--name-field-link-label')]/text()")
            content.append(file_pdf)

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
