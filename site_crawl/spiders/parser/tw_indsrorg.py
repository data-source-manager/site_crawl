# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class TW_indsrorgParser(BaseParser):
    name = 'tw_indsrorg'
    
    # 站点id
    site_id = "dced4adc-7638-42c8-8272-7c4b366ceca3"
    # 站点名
    site_name = "国防安全研究院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "dced4adc-7638-42c8-8272-7c4b366ceca3", "source_name": "国防安全研究院", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("135c7fa2-0607-4f41-1603-2496399e7ea8", "专题", "", "政治"),
            ("4a8e7b54-fe6f-11ec-a30b-d4619d029786", "专题/不对称作战", "https://indsr.org.tw/focuslist?uid=3", "政治"),
            ("4a8e8086-fe6f-11ec-a30b-d4619d029786", "专题/中共党政", "https://indsr.org.tw/focuslist?uid=3&typeId=22", "政治"),
            ("4a8e7d34-fe6f-11ec-a30b-d4619d029786", "专题/印太区域", "https://indsr.org.tw/focuslist?uid=3&typeId=32", "政治"),
            ("4a8e7c9e-fe6f-11ec-a30b-d4619d029786", "专题/台海形势", "https://indsr.org.tw/focuslist?uid=3&typeId=26", "政治"),
            ("4a8e7e1a-fe6f-11ec-a30b-d4619d029786", "专题/国际形势", "https://indsr.org.tw/focuslist?uid=3&typeId=27", "政治"),
            ("4a8e7dac-fe6f-11ec-a30b-d4619d029786", "专题/灰色行动", "https://indsr.org.tw/focuslist?uid=3&typeId=34", "政治"),
            ("4a8e7f96-fe6f-11ec-a30b-d4619d029786", "专题/资安威胁", "https://indsr.org.tw/focuslist?uid=3&typeId=18", "政治"),
            ("fa58d27b-d480-3eb0-9e70-6333b6da21d3", "国防安全", "", "政治"),
            ("4a8e79d8-fe6f-11ec-a30b-d4619d029786", "国防安全/即时评析", "https://indsr.org.tw/focuslist2?uid=11", "政治"),
            ("4a8e82e8-fe6f-11ec-a30b-d4619d029786", "国防情势特刊", "https://indsr.org.tw/republicationlist?uid=13", "政治"),
            ("4a8e81b2-fe6f-11ec-a30b-d4619d029786", "最新公告", "https://indsr.org.tw/informationlist?uid=7", "政治"),
            ("4a8e8270-fe6f-11ec-a30b-d4619d029786", "民意调查", "https://indsr.org.tw/safetyInvestigation?uid=45", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//div[contains(@class,'browse translate')]//div[@class='row']//a/@href|//div[@class='col-xs-12 col-sm-6 col-lg-4']/a/@href").extract() or ""
        if news_urls:
            for news_url in news_urls:
                if not news_url.startswith('http'):
                    news_url = urljoin('https://indsr.org.tw/', news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//div[contains(@class,'title')]/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_str = response.xpath(
            "//figcaption[@class='figure-caption']/a/text()|//div[@class='flex']/span[contains(@class,'colorb')]/text()").get()
        if author_str:
            authors.append(author_str.strip())
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='ps-3 bgg']/text()[normalize-space()]|"
                                  "//div[contains(@class,'time2')]/text()[normalize-space()]|"
                                  "//div[@class='book-text']/div[@class='subdate']/text()").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//a[@class='pe-3']/text()").getall()
        if tags:
            for tag in tags:
                tags_list.append(tag.strip())
        tags_list = list(set(tags_list))
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@class='article-text']/div[contains(@class,'font')]|//div[contains(@class,'img position-relative')]/img|//div[@class='text']/*|//div[@class='directory']/div/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'div']:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        pdf_src = response.xpath("//a[@class='hoverBtn']/@href").get()
        if pdf_src:
            file_dic = {
                "type": "file",
                "src": pdf_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(pdf_src) + ".pdf"
            }
            content.append(file_dic)
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

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.xpath("./@src").extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": None,
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
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
        if "respubcationmenus" in response.url:
            read_count_str = response.xpath("//div[@class='browse']//span/text()").get()
        else:
            read_count_str = response.xpath("//div[contains(@class,'number')]/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:

        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
