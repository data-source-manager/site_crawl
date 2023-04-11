# -*- coding: utf-8 -*-
# update:(liyun|2023-03-06) -> 板块核对与解析代码覆盖
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UkReutersParser(BaseParser):
    name = 'reuters'
    
    # 站点id
    site_id = "b821bec9-49ef-4538-a5bb-42a902f58d4a"
    # 站点名
    site_name = "路透社英文网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "b821bec9-49ef-4538-a5bb-42a902f58d4a", "source_name": "路透社英文网", "direction": "uk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9769c74b-c9d2-3f50-a08c-c10aa1271bc4", "世界", "", "政治"),
            ("c6223496-fddf-4b2e-b483-d4dcf00cd8c8", "世界/中东", "https://www.reuters.com/world/middle-east/", "政治"),
            ("4a8b34c6-fe6f-11ec-a30b-d4619d029786", "世界/中国", "https://www.reuters.com/world/china/", "政治"),
            ("4cb4b654-1f5a-4c5c-84ed-195a637abe11", "世界/亚太地区", "https://www.reuters.com/world/asia-pacific/", "政治"),
            ("08054ca8-1387-4367-8357-46150c28d9b9", "世界/印度", "https://www.reuters.com/world/india/", "政治"),
            ("4a8b3372-fe6f-11ec-a30b-d4619d029786", "世界/欧洲", "https://www.reuters.com/world/europe/", "政治"),
            ("4a8b3584-fe6f-11ec-a30b-d4619d029786", "世界/美国", "https://www.reuters.com/world/us/", "政治"),
            ("d40901a0-fce3-4a45-ba2d-5d1f01ab1085", "世界/美洲", "https://www.reuters.com/world/americas/", "政治"),
            ("4cd7175e-d260-4194-a3df-5e0b74e36f0b", "世界/英国", "https://www.reuters.com/world/uk/", "政治"),
            ("e999a901-fb28-49d5-a2b8-4527aa4bcc89", "世界/非洲", "https://www.reuters.com/world/africa/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@data-testid="Heading"]/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@name="article:author"]/@content').extract() or []]

    def get_pub_time(self, response) -> str:
        _time = response.xpath('//meta[@name="article:published_time"]/@content').extract_first()
        if _time:
            pub_time = datetime_helper.fuzzy_parse_timestamp(_time)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

    def get_tags(self, response) -> list:
        # return [a.strip() for a in response.xpath('').extract() or []]
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[contains(@class, "paywall-article")]/*'
            '|//div[@data-testid="primary-image"]//img'
            '|//div[@data-testid="Carousel"]//img'
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
                img_src = tag.attrib.get("src", "")
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