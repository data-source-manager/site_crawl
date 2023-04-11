# -*- coding: utf-8 -*-
# update:(2023-02-10) -> 板块核对与修复
# update:(liyun|2023-03-23) -> 仅解析最新数据
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwEttodayParser(BaseParser):
    name = 'ettoday'
    # 站点id
    site_id = "186d5a09-9995-4e5a-8237-d36fc80757f8"
    # 站点名
    site_name = "Ettoday民调云"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "186d5a09-9995-4e5a-8237-d36fc80757f8", "source_name": "Ettoday民调云", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4497c7ac-c69e-42ac-aefd-b898ffec13ee", "专题", "https://www.ettoday.net/survey/list.php?kind=13", "社会"),
            ("70fccf84-4dbd-4867-8133-1c6adc52dcfc", "产业财经", "https://www.ettoday.net/survey/list.php?kind=3", "经济"),
            ("04b4f12e-b72b-4f07-8bf6-a6bc6211381a", "军武", "https://www.ettoday.net/news/focus/%E8%BB%8D%E6%AD%A6/", "军事"),
            ("3ab2a857-d24d-4f61-9728-c0163a406ef8", "国际", "", "政治"),
            ("438f4a1e-0f05-4d89-833f-74c3efb77a0f", "国际/东南亚要闻", "https://www.ettoday.net/news/focus/%E6%96%B0%E8%81%9E%E9%9B%B2APP/%E6%9D%B1%E5%8D%97%E4%BA%9E%E8%A6%81%E8%81%9E/", "政治"),
            ("7d023d84-f889-4b18-aa89-0a1bd4ebc0ad", "国际/日韩要闻", "https://www.ettoday.net/news/focus/%E6%96%B0%E8%81%9E%E9%9B%B2APP/%E6%97%A5%E9%9F%93%E8%A6%81%E8%81%9E/", "政治"),
            ("a7e50132-eb89-4271-88ae-e46eadf94313", "国际/美洲要闻", "https://www.ettoday.net/news/focus/%E6%96%B0%E8%81%9E%E9%9B%B2APP/%E7%BE%8E%E6%B4%B2%E8%A6%81%E8%81%9E/", "政治"),
            ("47efc625-4662-4885-b75c-0999253cff9a", "大陆", "", "政治"),
            ("f01e6522-96f4-4652-845c-94bdc5f1f7dd", "大陆/军武", "https://www.ettoday.net/news/focus/%E8%BB%8D%E6%AD%A6/", "军事"),
            ("3bd0b7d9-9496-4495-955b-717997e3097c", "大陆/华闻", "https://www.ettoday.net/news/focus/%E5%A4%A7%E9%99%B8/%E8%8F%AF%E8%81%9E%E5%BF%AB%E9%81%9E/", "军事"),
            ("a2047aef-133a-439e-9968-ea9bc1806ad5", "政治", "https://www.ettoday.net/news/focus/%E6%94%BF%E6%B2%BB/", "政治"),
            ("2ca7ecee-b171-49b9-8b87-dda8a594195c", "政治調查成果", "https://www.ettoday.net/survey/list.php?kind=8", "政治"),
            ("16f5f06e-0671-46fa-bef2-4a27b1d2d2e9", "新闻时事", "https://www.ettoday.net/survey/list.php?kind=1", "政治"),
            ("957cbdf3-406b-4be0-892a-6ca05f05aa83", "生活综合", "https://www.ettoday.net/survey/list.php?kind=2", "社会"),
            ("3079ed83-6c0a-4228-a125-d2c5f49f2058", "美食旅游", "https://www.ettoday.net/survey/list.php?kind=6", "社会"),
            ("6eadf677-c3e7-47a6-9557-c8a369ce5b06", "购物消费", "https://www.ettoday.net/survey/list.php?kind=5", "社会"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    # update:(liyun|2023-03-23) -> 仅解析最新数据
    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="box_2"]//h2/a/@href'
            '|//div[@class="block_content"]//div[@class="piece clearfix"]/h3/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            news_url = urljoin(response.url, news_url)
            if news_url.startswith("https://www.ettoday.net/"):
                yield news_url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("|", 1)[
            0].strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@name="DC.Publisher"]/@content').extract() or []]

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
                '//div[@class="box_0"]/*'
                '|//div[@class="box_0"]/p/img'
                '|//div[@class="story"]/*'
                '|//div[@class="story"]//img'
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
                img_src = img_src.split("?")[0].strip()
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
        return "zh-CN"

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
