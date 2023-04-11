# -*- coding: utf-8 -*-
# update:(liyun|2023-02-06) -> 板块核对与解析代码覆盖
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaDniParser(BaseParser):
    name = 'usa_dni'
    
    # 站点id
    site_id = "7a5607d7-b603-4984-bf66-eccb9d95e201"
    # 站点名
    site_name = "国家反恐中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7a5607d7-b603-4984-bf66-eccb9d95e201", "source_name": "国家反恐中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("ac98ad11-68bd-40bc-83c8-fc8b2c7046a0", "NCTC新闻室", "https://www.dni.gov/index.php/nctc-newsroom", "政治"),
            ("b90a2078-444e-4e63-b33a-23f306d27701", "我们所做的", "https://www.dni.gov/index.php/nctc-what-we-do", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        # 板块特殊处理(我们所做的)
        if response.url.lower() == "https://www.dni.gov/index.php/nctc-what-we-do":
            yield "https://www.dni.gov/index.php/nctc-what-we-do"
        news_urls = response.xpath('//h3[@class="catItemTitle"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="title"]/@content').extract_first(default="").strip()
        # 板块特殊处理(我们所做的)
        if response.url.startswith("https://www.dni.gov/index.php/nctc-what-we-do"):
            title = "nctc-what-we-do"
        return title

    def get_author(self, response) -> list:
        author = response.xpath('//div[@class="itemCategory"]/a/text()').extract_first(default="").strip()
        return [author] if author else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[@class="itemDateCreated"]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        # 解析正文数据
        for tag in response.xpath(
                '//div[@class="itemFullText"]/*'
                '|//div[@class="itemImageBlock"]//img'
                '|//div[@itemprop="articleBody"]/*'
                '|//div[@itemprop="articleBody"]//img'
                '|//div[@itemprop="articleBody"]//iframe'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3"]:
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
            # 解析视频
            elif tag.root.tag == "iframe":
                video_url = tag.attrib.get("src")
                if not video_url:
                    continue
                content.append({
                    "type": "video",
                    "src": video_url,
                    "name": None,
                    "md5src": self.get_md5_value(video_url) + f'.mp4',
                    "description": None,
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
