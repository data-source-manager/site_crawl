# Name: (香港观察)站点解析器开发
# Date: 2023-02-14
# Author: liyun
# Desc: None


import time
from urllib.parse import urljoin

import langdetect

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class HkHongkongwatcHParser(BaseParser):
    name = 'hongkongwatch'
    
    # 站点id
    site_id = "438cb681-99ce-43da-bae3-4b2fe9ec409e"
    # 站点名
    site_name = "香港观察"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "438cb681-99ce-43da-bae3-4b2fe9ec409e", "source_name": "香港观察", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("fdfebe22-b264-4a5b-af2e-d109d6a7fa59", "事件", "https://www.hongkongwatch.org/events", "政治"),
            ("6e70124b-d349-4108-93fe-e1be1b3bfb58", "政治犯", "", "政治"),
            ("63c18b3c-f86e-4246-8132-25143ca9047a", "政治犯/关于政治犯运动", "https://www.hongkongwatch.org/pol-prisoners", "政治"),
            ("9905efff-b3ed-4c97-a59e-aa0bfe28cc29", "政治犯/新闻自由运动", "https://www.hongkongwatch.org/press-freedom-campaign", "政治"),
            ("852d6db0-d2df-4ff2-81ee-3996f1918811", "活动", "", "政治"),
            ("493bd213-9d7b-43db-a76f-d24b4ae8d685", "活动/不引渡到香港", "https://www.hongkongwatch.org/extradition", "政治"),
            ("6d391e1e-1ff4-4397-96dc-a58998eb958d", "活动/欧盟-中国", "https://www.hongkongwatch.org/euchina", "政治"),
            ("c5d26cbe-0020-482a-8641-752b61cf0b3b", "活动/红色资本", "https://www.hongkongwatch.org/red-capital", "政治"),
            ("2d109e6f-aa4e-4100-8ce4-b7575536aba9", "活动/联合国", "https://www.hongkongwatch.org/united-nations", "政治"),
            ("15b717f1-090a-401c-b6ff-0162afd541f0", "消息", "https://www.hongkongwatch.org/latest-news", "政治"),
            ("4a8e42b0-fe6f-11ec-a30b-d4619d029786", "研究", "", "政治"),
            ("7bddc85c-4906-4bcc-91cc-e2b03fd64ce1", "研究/所有研究、分析观点", "https://www.hongkongwatch.org/research", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        # 特殊处理: 非列表页板块
        if response.url in [
            "https://www.hongkongwatch.org/pol-prisoners",
            "https://www.hongkongwatch.org/press-freedom-campaign"
        ]:
            yield response.url
        # 列表页板块
        news_urls = response.xpath(
            '//div[@class="summary-title"]/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("—")[0].strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@itemprop="author"]/@content').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(datetime_helper.fuzzy_parse_timestamp(_time))))
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        # return [a.strip() for a in response.xpath('').extract() or []]
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//section[@class="Main-content"]//div[@class="sqs-block-content"]/*'
                '|//section[@class="Main-content"]//div[@class="sqs-block-content"]//img'
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
