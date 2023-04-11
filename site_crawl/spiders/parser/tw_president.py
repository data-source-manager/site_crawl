# -*- coding: utf-8 -*-
# update:(liyun|2023-03-15) -> 板块核对与解析代码修正
import re
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class PresidentParser(BaseParser):
    name = 'tw_president'

    
    # 站点id
    site_id = "3bd3a833-b5e3-4c4d-8ddd-5ba7e68583c2"
    # 站点名
    site_name = "中华民国总统府"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "3bd3a833-b5e3-4c4d-8ddd-5ba7e68583c2", "source_name": "中华民国总统府", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("6759cac5-4658-3ac8-9413-97701798472f", "新闻与活动", "", "政治"),
            ("d51f77af-d8ac-415e-8828-ad7f1740c58b", "新闻与活动/总统府新闻", "https://www.president.gov.tw/Page/35", "政治"),
            ("7544b512-3d1a-3d39-8fda-c7b7fe83cb66", "新闻与活动/每日活动行程", "https://www.president.gov.tw/Page/37", "政治"),
            ("d37bd7b1-3bbc-3341-8fef-b1bfbd8d19de", "焦点议题", "", "政治"),
            ("fe978e68-c3c3-4943-a04e-bfe67eeb9bfc", "焦点议题/两岸", "https://www.president.gov.tw/Issue/72", "政治"),
            ("1ff9cfe4-345a-388d-bc1b-5634fea10314", "焦点议题/人权", "https://www.president.gov.tw/Issue/70", "政治"),
            ("0b803e22-cfdb-421f-a8c2-169fd3bdab73", "焦点议题/创新经济", "https://www.president.gov.tw/Issue/60", "经济"),
            ("63a2484c-5ee6-3523-b644-d4bfd8870192", "焦点议题/前沿基础建设", "https://www.president.gov.tw/Issue/335", "政治"),
            ("5884b61c-cb41-394b-b689-bd6dde66e471", "焦点议题/司法改革", "https://www.president.gov.tw/Issue/64", "政治"),
            ("9cdce917-9c02-4ecb-842a-5dbb0d7c058f", "焦点议题/国防", "https://www.president.gov.tw/Issue/74", "军事"),
            ("13fff35b-9469-4069-ba56-d20d083780f8", "焦点议题/外交", "https://www.president.gov.tw/Issue/76", "政治"),
            ("6aa7dad3-11db-38cb-8bda-8ec911068193", "焦点议题/灾害防救", "https://www.president.gov.tw/Issue/404", "政治"),
            ("8e0f6872-d195-393f-a681-946dae49752b", "焦点议题/社会住宅", "https://www.president.gov.tw/Issue/613", "政治"),
            ("17bd696c-9eb6-3c4c-9b09-021569483932", "焦点议题/绿色能源", "https://www.president.gov.tw/Issue/430", "政治"),
            ("94509160-415e-42fd-af24-793bccc8be33", "焦点议题/重要谈话", "https://www.president.gov.tw/Issue/58", "政治"),
            ("260885a5-db2f-32fd-834f-8e2ad6333ad6", "焦点议题/长照", "https://www.president.gov.tw/Issue/375", "政治"),
            ("a1940250-fe79-3842-a510-d879fab42766", "焦点议题/防疫", "https://www.president.gov.tw/Issue/471", "政治"),
            ("f1aca243-29fe-35d7-8026-5b8a5d85bf1e", "焦点议题/青年", "https://www.president.gov.tw/Issue/565", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "3bd3a833-b5e3-4c4d-8ddd-5ba7e68583c2"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//ul[@id="grid"]/li/a/@href'
            '|//div[@class="row"]/p/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@name="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//span[@class="date_green"]/text()').extract_first(default="").strip()
            y, m, d = re.findall(r"\d+", publish_date)
            publish_date = datetime_helper.parseTimeWithOutTimeZone(
                datetime.strptime(f'{1911 + int(y)}-{m}-{d}', '%Y-%m-%d'),
                site_name="中华民国总统府"
            )
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//div[@class="president"]/div/div/*'
                '|//div[@class="president"]//img'
                '|//div[@class="container"]//iframe'
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
                # if (not img_src.startswith('http')) or (suffix not in ["jpg", 'png', 'jpeg']):
                if (not img_src.startswith('http')):
                    continue
                content.append({
                    "type": "image",
                    "src": img_src,
                    "name": tag.attrib.get('alt', "").strip(),
                    "md5src": self.get_md5_value(img_src) + f'.jpg',
                    "description": tag.xpath("../figcaption/text()").extract_first(default="").strip(),
                })
            # 解析视频
            elif tag.root.tag == "iframe":
                video_src = tag.attrib.get("src")
                if "www.youtube.com" not in video_src:
                    continue
                content.append({
                    "type": "video",
                    "src": video_src,
                    "name": None,
                    "description": None,
                    "md5src": self.get_md5_value(video_src) + ".mp4"
                })
            else:
                pass
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

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
