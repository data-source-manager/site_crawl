# -*- coding: utf-8 -*-
# update:(liyun|20230215) -> 站点板块核对与修复
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class HkAasTocKsParser(BaseParser):
    name = 'hk_aastocks'
    
    # 站点id
    site_id = "90227829-0e6a-48d7-ad88-717b9cae3f11"
    # 站点名
    site_name = "阿思达克财经网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "90227829-0e6a-48d7-ad88-717b9cae3f11", "source_name": "阿思达克财经网", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("2ee1b454-8df0-4b37-96fe-1a06ff2b966e", "新闻", "http://www.aastocks.com/tc/stocks/news/aafn", "经济"),
            ("4a8e43dc-fe6f-11ec-a30b-d4619d029786", "财经新闻", "http://www.aastocks.com/tc/stocks/news/aafn/latest-news", "经济"),
            ("db0ad2c7-9daf-4a7d-8423-38c17019bac3", "财经视频", "", "政治"),
            ("c5652368-3e67-45b8-8572-40bca15282d7", "财经视频/财经焦点", "http://www.aastocks.com/aatv/category/list?group=1", "经济"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        if response.url == "http://www.aastocks.com/aatv/category/list?group=1":
            news_urls = [
                f'http://www.aastocks.com/aatv/video/{tag.attrib.get("data-vid")}/{tag.attrib.get("data-catg")}'
                for tag in response.xpath('//a[@class="linkVideo-a"]')
                if tag.attrib.get("data-vid")
            ]
        else:
            news_urls = response.xpath('//a[contains(@id, "cp_ucAAFNSearch_repNews_lnkNews")]/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        _time = response.xpath('//meta[@name="aa-update"]/@content').extract_first()
        if _time:
            _time = str(
                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(datetime_helper.fuzzy_parse_timestamp(_time))))
        else:
            _time = response.xpath('//div[@class="newsDate"]/text()').extract_first(default="").strip()
            _time = f'{_time} 00:00:00'
        return _time or "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 处理视频板块
        if response.url.startswith("http://www.aastocks.com/aatv/video/"):
            # 解析视频资源
            video_src = re.search("sVideoUrl = \'(.+?)\'", response.text).groups()[0].split("?")[0]
            suffix = video_src.split(".")[-1].lower()
            desc = response.xpath('//div[@id="screen"]//div[@class="content"]/text()').extract_first(default="").strip()
            desc and content.append({"data": desc, "type": "text"})
            content.append({
                "type": "video",
                "src": video_src,
                "name": response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip(),
                "md5src": self.get_md5_value(video_src) + f'.{suffix}',
                "description": desc,
            })
        else:
            # 解析正文数据
            for tag in response.xpath(
                    '//div[@id="spanContent"]/span/p'
                    '|//img[@id="cp_ucAAFNContent_imgContentNewsImage"]'
            ) or []:
                # 解析段落文本
                if tag.root.tag == "p":
                    for text in tag.xpath(".//text()").extract() or []:
                        text = text.strip()
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
        return "zh-cn"

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
