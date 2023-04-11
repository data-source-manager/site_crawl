# -*- coding: utf-8 -*-
# update:(liyun|2023-03-14) -> 板块核对与解析代码覆盖
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TW_wenxuecityParser(BaseParser):
    name = 'tw_wenxuecity'
    # 站点id
    site_id = "c5a1473f-c28d-41f8-88cf-34b4c5b98d9e"
    # 站点名
    site_name = "文学城新闻网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c5a1473f-c28d-41f8-88cf-34b4c5b98d9e", "source_name": "文学城新闻网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("ed7919a0-a2b6-48c7-af24-1a41abb0bf80", "新闻", "https://www.wenxuecity.com/news/", "政治"),
            ("4a8ea124-fe6f-11ec-a30b-d4619d029786", "新闻/焦点新闻", "https://www.wenxuecity.com/news/morenews/", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="wrapper"]/ul/li/a/@href'
            '|//div[@id="contentList"]/ul/li/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("|")[0].strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//span[@itemprop="author"]/text()').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//time[@itemprop="datePublished"]/@datetime').extract_first(default="").strip()
            publish_date = datetime_helper.parseTimeWithTimeZone(publish_date)
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//article[@id="articleContent"]/*/text()'
        ) or []:
            # 解析段落文本
            if isinstance(tag.root, str):
                text = tag.root.strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
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
        return "zh"

    def get_like_count(self, response) -> int:
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        try:
            return int(response.xpath('//span[@id="countnum"]/text()').extract_first(default=0))
        except:
            return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
