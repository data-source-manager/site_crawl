# -*- coding: utf-8 -*-
# update:(liyun|2023-02-03) -> 板块核对与解析代码修正
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class KH_jianhuadailyParser(BaseParser):
    name = 'kh_jianhuadaily' 

    # 站点id
    site_id = "97618438-ded5-453a-a27e-8b877c7b5e41"
    # 站点名
    site_name = "柬华日报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "97618438-ded5-453a-a27e-8b877c7b5e41", "source_name": "柬华日报", "direction": "kh", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8cef32-fe6f-11ec-a30b-d4619d029786", "中国国际", "https://jianhuadaily.com/%e4%b8%ad%e5%9b%bd%e5%9b%bd%e9%99%85", "政治"),
            ("4a8cef33-fe6f-11ec-a30b-d4619d029786", "华社动态", "https://jianhuadaily.com/%e5%8d%8e%e7%a4%be%e5%8a%a8%e6%80%81", "政治"),
            ("faff9c64-36fc-3857-b800-67ad9ce13a09", "柬华新闻", "", "政治"),
            ("4a8cedf2-fe6f-11ec-a30b-d4619d029786", "柬华新闻/商业经济", "https://jianhuadaily.com/%e5%8d%8e%e7%a4%be%e5%8a%a8%e6%80%81/%e5%95%86%e4%b8%9a%e7%bb%8f%e6%b5%8e", "经济"),
            ("4a8cee9b-fe6f-11ec-a30b-d4619d029786", "柬华新闻/新冠肺炎", "https://jianhuadaily.com/%e5%8d%8e%e7%a4%be%e5%8a%a8%e6%80%81/%e6%96%b0%e5%86%a0%e8%82%ba%e7%82%8e", "政治"),
            ("4a8cecc6-fe6f-11ec-a30b-d4619d029786", "柬华新闻/时政要闻", "https://jianhuadaily.com/%e5%8d%8e%e7%a4%be%e5%8a%a8%e6%80%81/%e6%97%b6%e6%94%bf%e8%a6%81%e9%97%bb", "政治"),
            ("4a8cee9c-fe6f-11ec-a30b-d4619d029786", "柬华新闻/社会新闻", "https://jianhuadaily.com/%e5%8d%8e%e7%a4%be%e5%8a%a8%e6%80%81/%e7%a4%be%e4%bc%9a%e6%96%b0%e9%97%bb", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h2[@class="title"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        authors = response.xpath('//span[@class="post-author-name"]/b/text()').extract() or []
        return [a.split("：")[-1].strip() for a in authors]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//time[@class="post-published updated"]/@datetime').extract_first()
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
                '//div[@class="entry-content clearfix single-post-content"]/*'
                '|//div[@class="entry-content clearfix single-post-content"]/p//img'
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
        return "zh"

    def get_like_count(self, response) -> int:
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        try:
            read_count_text = response.xpath('//span[contains(@class,"post-meta-views")]/text()').extract_first(
                default="").strip()
            return int(re.search(r'\d+', read_count_text.replace(',', "")).group())
        except:
            return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
