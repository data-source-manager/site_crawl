# Name: (Ettoday云论)站点解析器开发
# Date: 2023-02-10
# Author: liyun
# Desc: None


import time
from urllib.parse import urljoin

import langdetect

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwForum_ettodayParser(BaseParser):
    name = 'forum_ettoday'
    # 站点id
    site_id = "126d5a09-9995-4e5a-8237-d36fc80757f8"
    # 站点名
    site_name = "Ettoday云论"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "126d5a09-9995-4e5a-8237-d36fc80757f8", "source_name": "Ettoday云论", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("541af6f7-8d46-4dc1-9301-21095d952bb9", "两岸观察", "https://forum.ettoday.net/newslist/285", "政治"),
            ("6f533e69-dbe4-4f3a-b345-087c5e2c8f54", "司法人权", "https://forum.ettoday.net/newslist/679", "政治"),
            ("2f257a3e-9059-4faf-b73f-6b1d06e2285b", "国防军武", "https://forum.ettoday.net/newslist/282", "军事"),
            ("235ba4c2-7e8e-4c44-bd3f-0498533376f4", "政治外交", "https://forum.ettoday.net/newslist/677", "政治"),
            ("6c4de898-1bfc-4289-bf94-c7958657c57f", "行动法庭", "https://forum.ettoday.net/newslist/680", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="c1"]//h2/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("|")[0].strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        _time = response.xpath('//meta[@name="pubdate"]/@content').extract_first()
        if _time:
            pub_time = datetime_helper.fuzzy_parse_timestamp(_time)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//div[@itemprop="articleBody"]/*'
                '|//div[@itemprop="articleBody"]/p/img'
                '|//div[@itemprop="articleBody"]//iframe'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                # 段尾
                if text[:4] in ["熱門推薦", "系列報導", "好文推薦", "推薦影音"]:
                    break
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
                video_src = tag.attrib.get("src", "")
                if not video_src.startswith("https://www.youtube.com/"):
                    continue
                content.append({
                    "type": "video",
                    "src": video_src,
                    "name": tag.attrib.get('alt', "").strip(),
                    "md5src": self.get_md5_value(video_src) + f'.mp4',
                    "description": "",
                })
            else:
                pass
        return content

    def get_detected_lang(self, response) -> str:
        return langdetect.detect(f"{self.get_title(response)}")

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
