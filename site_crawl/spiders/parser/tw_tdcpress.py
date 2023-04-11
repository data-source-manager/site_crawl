# Name: 站点(台湾数位汇流网)解析器开发
# Date: 2023-03-08
# Author: liyun
# Desc: None


import json
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwTdcpressParser(BaseParser):
    name = 'wt_tdcpress'
    
    # 站点id
    site_id = "54a38377-68ab-4d10-a7bf-3536d1a6c035"
    # 站点名
    site_name = "台湾数位汇流网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "54a38377-68ab-4d10-a7bf-3536d1a6c035", "source_name": "台湾数位汇流网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("42b3794e-c2e9-3270-9dc3-c959fc2837b4", "国际", "", "政治"),
            ("578453c5-a878-49ca-b676-54c995db3785", "国际/媒体并购", "https://www.tdcpress.com/Article/Category/4?tag=25", "政治"),
            ("4a8ccf34-fe6f-11ec-a30b-d4619d029786", "政策", "", "政治"),
            ("9ab6110f-43ed-4996-a5c1-c7e82bb8514f", "政策/法规新讯", "https://www.tdcpress.com/Article/Category/6?tag=36", "政治"),
            ("e700d6ca-7607-11ed-ad4d-d4619d029786", "政策/解读法令", "https://www.tdcpress.com/Article/Category/6?tag=39", "政治"),
            ("4da84c36-77a5-44f2-8d08-daf7e0daa60b", "焦点", "", "政治"),
            ("1e0243fb-7502-4d49-8328-5ac64eb7bf85", "焦点/新闻快讯", "https://www.tdcpress.com/Article/Category/2?tag=1074", "社会"),
            ("218cd79e-46d8-4a58-b62a-e6a18d79c74a", "焦点/新闻现场", "https://www.tdcpress.com/Article/Category/2?tag=7", "社会"),
            ("8e52d603-8771-4faa-998f-46b2a72f3594", "焦点/新闻短波", "https://www.tdcpress.com/Article/Category/2?tag=68", "社会"),
            ("7531db9a-9c32-3893-b017-61e0c8b8b212", "评论", "", "政治"),
            ("c1391051-27ab-4202-b05b-b755b075d5de", "评论/政策观察", "https://www.tdcpress.com/Article/Category/7?tag=44", "政治"),
            ("4a8cd06a-fe6f-11ec-a30b-d4619d029786", "评论/政经时事", "https://www.tdcpress.com/Article/Category/7?tag=43", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.method = 'post'

    def parse_list(self, response) -> list:
        response.meta['method'] = 'get'
        news_urls = [f'https://www.tdcpress.com/Article/Index/{data["Id"]}' for data in json.loads(response.text)]
        for news_url in list(set(news_urls)):
            yield news_url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//div[@class="author-tp-2"]/span/text()').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//div[@class="date-tp-4"]/span/text()').extract_first()
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(datetime_helper.fuzzy_parse_timestamp(_time))))
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return [a.strip() for a in response.xpath('//ul[@class="post-tags-list"]/li/a/text()').extract() or []]

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="contentWrapper"]/*'
            '|//div[@class="post-main-img"]/img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                # 正文截断标记
                if text.startswith('更多台灣數位匯流網報導'):
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
