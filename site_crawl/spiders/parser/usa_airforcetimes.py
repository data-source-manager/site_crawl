# Name: (空军时报)站点解析器开发
# Date: 2023-02-13
# Author: liyun
# Desc: None

import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaAirforcetimesParser(BaseParser):
    name = 'airforcetimes'
    
    # 站点id
    site_id = "fc2f8fde-bbb5-4df0-8ee8-26f087b86066"
    # 站点名
    site_name = "空军时报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "fc2f8fde-bbb5-4df0-8ee8-26f087b86066", "source_name": "空军时报", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("5117ee34-66bf-4017-ad5d-274e0abecdfb", "消息", "https://www.airforcetimes.com/news/", "军事"),
            ("4a8e14ca-fe6f-11ec-a30b-d4619d029786", "消息/五角大楼与国会", "https://www.airforcetimes.com/news/pentagon-congress/", "军事"),
            ("4a8e1498-fe6f-11ec-a30b-d4619d029786", "消息/你的空军", "https://www.airforcetimes.com/news/your-air-force/", "军事"),
            ("d13b4f0b-9311-4ad2-b8ae-3a5db2a1bb86", "闪点", "https://www.airforcetimes.com/flashpoints/", "军事"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h5/a/@href|//h6[@itemprop="headline"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            news_url = urljoin(response.url, news_url)
            if news_url.startswith('https://www.airforcetimes.com/video/'):
                continue
            yield news_url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@property="og:author"]/@content').extract() or []]

    def get_pub_time(self, response) -> str:
        _time = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if _time:
            pub_time = datetime_helper.fuzzy_parse_timestamp(_time)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return [a.strip() for a in
                response.xpath('//div[@class="default__Wrapper-sc-110354g-0 dpwnWn"]/a/@title').extract() or []]

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//main/div/article/*'
                '|//main/div/div/div/figure//picture/img'
                '|//section/div/article/*'
                '|//section/div/div/div/figure//picture/img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
            elif tag.root.tag == "div":
                # 正文段落结尾标记
                if tag.attrib.get("class", "").startswith("ShareBar__Wrapper"):
                    break
                for text in tag.xpath(".//text()").extract() or []:
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
        return 'en-US'

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
