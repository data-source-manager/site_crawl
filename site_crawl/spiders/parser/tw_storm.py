# -*- coding: utf-8 -*-
# update:(liyun|2023-03-06) -> 板块核对与解析代码覆盖
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwStormParser(BaseParser):
    name = 'storm'
    
    # 站点id
    site_id = "ddea91a0-abb6-40e0-9ea6-89f027f34652"
    # 站点名
    site_name = "风传媒"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "ddea91a0-abb6-40e0-9ea6-89f027f34652", "source_name": "风传媒", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("6efda594-ef66-4443-9133-a929850da58a", "下班经济学", "https://www.storm.mg/category/164654", "经济"),
            ("a23975e8-7ac1-4820-a651-97ec682d4088", "国际", "https://www.storm.mg/category/117", "政治"),
            ("4a8ee666-fe6f-11ec-a30b-d4619d029786", "政治", "https://www.storm.mg/category/118", "政治"),
            ("fbe4dfcc-581c-4c33-83ee-67393e0d3da5", "政策盘点", "https://www.storm.mg/category", "政治"),
            ("4a9bfa71-9194-4ef9-9cda-d289a59f0102", "评论", "https://www.storm.mg/category/2", "社会"),
            ("9ddf8f4c-6fa5-4cea-812b-b8ed1fe39d7a", "重磅财经", "https://www.storm.mg/category/23083", "经济"),
            ("94ffc39e-1dee-46fc-a8eb-76bb8b7b0526", "风影音", "https://www.storm.mg/video", "其他"),
            ("4147d013-5230-4483-be8e-d02a1e283079", "风生活", "https://www.storm.mg/lifestyles", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@id="category_content"]//a[@class="card_link link_title"]/@href'
            '|//div[@id="category_top"]//a[@class="card_link link_title"]/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath(
            '//span[@class="author_text"]/text()'
            '|//meta[@property="dable:author"]/@content'
        ).extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
            return datetime_helper.parseTimeWithTimeZone(_time)
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//div[@id="CMS_wrapper"]//p'
                '|//div[@class="feature_img_wrapper"]//img'
                '|//img[@id="feature_img"]'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
            # 解析图像数据
            elif tag.root.tag == "img":
                img_src = tag.attrib.get("srcset", "") or tag.attrib.get("src", "")
                if not img_src:
                    continue
                img_src = img_src.split("?")[0].split(" ")[0]
                img_src = urljoin(response.url, img_src)
                suffix = img_src.split(".")[-1].lower()
                if (not img_src.startswith('http')) or (suffix not in ["jpg", 'png', 'jpeg']):
                    continue
                content.append({
                    "type": "image",
                    "src": img_src,
                    "name": tag.attrib.get('alt', "").strip(),
                    "md5src": self.get_md5_value(img_src) + f'.{suffix}',
                    "description": tag.xpath("../figcaption/text()").extract_first(default="").strip(),
                })
            else:
                pass
        return content

    def get_detected_lang(self, response) -> str:
        return 'zh-cn'

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
