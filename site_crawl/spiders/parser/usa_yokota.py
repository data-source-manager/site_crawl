# -*- coding: utf-8 -*-
# update:(liyun:2023-02-02) -> 板块核对与解析代码修正
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaYoKoTaParser(BaseParser):
    name = 'usa_yokota'
    
    # 站点id
    site_id = "bb990b8e-432f-4ccf-b358-d13aa28a80f1"
    # 站点名
    site_name = "横田空军基地"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "bb990b8e-432f-4ccf-b358-d13aa28a80f1", "source_name": "横田空军基地", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8e2280-fe6f-11ec-a30b-d4619d029786", "最新消息", "https://www.yokota.af.mil/News/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h1/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        author = response.xpath('//div[@class="meta"]/ul/li[2]/text()').extract_first(default="").strip().strip("By ")
        return [author] if author else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//time/@datetime').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags = response.xpath('//footer/a/text()').extract() or []
        return [t.strip() for t in tags]

    def get_content_media(self, response) -> list:
        content = []
        # 解析图像
        for img_url in response.xpath('//ul[@class="slides"]/li/figure/a/@href').extract() or []:
            img_url = urljoin(response.url, img_url)
            suffix = img_url.split("?")[0].split(".")[-1].lower()
            if not suffix.startswith("http") and suffix not in ["jpg", "jpeg", "png"]:
                continue
            content.append({
                "type": "image",
                "src": img_url,
                "name": "",
                "md5src": self.get_md5_value(img_url) + f'.{suffix}',
                "description": None,
            })
        # 解析正文文本
        if response.xpath('//section[@class="article-detail-content"]/p'):
            for p in response.xpath('//section[@class="article-detail-content"]/p'):
                for text in p.xpath(".//text()").extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
        else:
            for p in response.xpath('//section[@class="article-detail-content"]//text()').extract():
                text = p.strip()
                text and content.append({"data": text, "type": "text"})

        return content

    def get_detected_lang(self, response) -> str:
        return "en-US"

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
