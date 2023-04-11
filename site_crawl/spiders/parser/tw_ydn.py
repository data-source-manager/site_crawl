# -*- coding: utf-8 -*-
# update:(liyun:2023-03-07) -> 新增板块与解析代码覆盖
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwYdnParser(BaseParser):
    name = 'ydn'
    
    # 站点id
    site_id = "d8c68242-384f-4dd0-86c0-8f7a423cd0c7"
    # 站点名
    site_name = "国防部青年日报社军事新闻网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "d8c68242-384f-4dd0-86c0-8f7a423cd0c7", "source_name": "国防部青年日报社军事新闻网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("1197e11b-78d5-4a52-893e-bb9b40535d2e", "军视界", "https://www.ydn.com.tw/news/newsFirst?type=vision", "军事"),
            ("f0d67cde-6b46-3a20-bb99-00642e07f25b", "军闻", "https://www.ydn.com.tw/news/newsFirst?type=military", "军事"),
            ("4a8cbea4-fe6f-11ec-a30b-d4619d029786", "军闻/国防焦点", "https://www.ydn.com.tw/news/newsList?typeId=10201", "军事"),
            ("4a8cc138-fe6f-11ec-a30b-d4619d029786", "军闻/武备巡礼", "https://www.ydn.com.tw/news/newsList?typeId=41", "军事"),
            ("4a8cc26e-fe6f-11ec-a30b-d4619d029786", "军闻/穿军服，赞", "https://www.ydn.com.tw/news/newsList?typeId=10207", "军事"),
            ("4a8cbfe4-fe6f-11ec-a30b-d4619d029786", "军闻/精锐新国军", "https://www.ydn.com.tw/news/newsList?typeId=10202", "军事"),
            ("c609b876-f8e3-4524-b1ab-5dafea234a14", "副刊", "https://www.ydn.com.tw/news/newsFirst?type=supplement", "社会"),
            ("4a8cbdaa-fe6f-11ec-a30b-d4619d029786", "即时", "https://www.ydn.com.tw/news/newsFirst?type=immediate", "政治"),
            ("26eab6aa-5942-4b07-9491-103d5010eaed", "寰宇安全", "https://www.ydn.com.tw/news/newsFirst?type=universal", "政治"),
            ("92d287b1-bdcb-4225-8d2c-373a2ccc9953", "社论", "https://www.ydn.com.tw/news/newsFirst?type=forum", "其他"),
            ("4a8cbe2c-fe6f-11ec-a30b-d4619d029786", "要闻", "https://www.ydn.com.tw/news/newsFirst?type=highlight", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@class="news-list-block"]/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("|")[0].strip()

    def get_author(self, response) -> list:
        try:
            author = response.xpath('//div[@class="newspage-content"]/div/p[1]/text()').extract_first(default="")
            if not author.startswith("記者"):
                return []
            author = author.strip("記者").split("／")[0]
            return [author]            
        except:
            return []

    def get_pub_time(self, response) -> str:
        try:
            pub_time = response.xpath('//span[contains(@class,"news-title-date")]//text()').extract_first(default="")
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub_time)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return [a.strip() for a in response.xpath('//button[@class="hashTag"]/text()').extract() or []]

    def get_content_media(self, response) -> list:
        content = []
        # 图像去重集
        img_duplicate_set = set()
        # 解析图像
        for tag in response.xpath(
            '//div[@class="slick-track"]//img'
            '|//div[@class="slick-list"]//div[contains(@class, "newspage-slick-big-img")]'
        ):
            try:
                img_src = ""
                name = None
                description = None
                # 从img标签提取
                if tag.root.tag == "img":
                    img_src = tag.attrib.get("srcset", "") or tag.attrib.get("src", "")
                    name = tag.attrib.get('alt', "").strip()
                    description = tag.xpath("../figcaption/text()").extract_first(default="").strip()
                # 从div标签style字段提取
                else:
                    img_src = re.search(r'background:url\((.+?)\)', tag.attrib.get("style")).groups()[0]
                # 空值校验与去重
                if (not img_src) or (img_src in img_duplicate_set):
                    continue
                img_duplicate_set.add(img_src)
                # 提取后缀
                img_src = urljoin(response.url, img_src).replace("&width=800", "")
                suffix = img_src.split(".")[-1].lower()
                # 格式校验
                if (not img_src.startswith('http')) or (suffix not in ["jpg", 'png', 'jpeg']):
                    continue
                content.append({
                    "type": "image",
                    "src": img_src,
                    "name": name,
                    "md5src": self.get_md5_value(img_src) + f'.{suffix}',
                    "description": description,
                })
            except:
                pass
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="newspage-content"]/div[1]/*'
            '|//div[@class="slick-track"]//img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
            else:
                pass
        return content

    def get_detected_lang(self, response) -> str:
        return 'zh-cn'
   
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
