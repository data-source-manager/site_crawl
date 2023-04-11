# -*- coding: utf-8 -*-
# update:(liyun|2023-02-02) -> 板块核对与修正
# PS: 该站点有ip访问频率检测
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class KP_dailynkParser(BaseParser):
    name = 'kp_dailynk'
    
    # 站点id
    site_id = "68eb8fa4-cbc6-43f5-9c69-3e6c3c8f592a"
    # 站点名
    site_name = "每日朝鲜"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "68eb8fa4-cbc6-43f5-9c69-3e6c3c8f592a", "source_name": "每日朝鲜", "direction": "kp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("a1893ca9-7b52-41a0-be76-502056d540dc", "主张", "https://www.dailynk.com/chinese/category/%e4%b8%bb%e5%bc%a0/", "政治"),
            ("248fbc8c-1ba2-437f-8123-f3751d6a7341", "新闻", "https://www.dailynk.com/chinese/category/%e6%96%b0%e9%97%bb/", "政治"),
            ("b1a77f30-207e-4ab9-94d6-562ba7941360", "朝鲜", "", "政治"),
            ("ede98114-6ab2-4d47-8eb3-1cbdd7ffd04a", "朝鲜/朝鲜内况", "https://www.dailynk.com/chinese/category/%e6%9c%9d%e9%b2%9c/%e6%9c%9d%e9%b2%9c%e5%86%85%e5%86%b5/", "政治"),
            ("4a8da27e-fe6f-11ec-a30b-d4619d029786", "消息", "https://www.dailynk.com/category/%eb%89%b4%ec%8a%a4/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}
        self.site_id = '68eb8fa4-cbc6-43f5-9c69-3e6c3c8f592a'

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h3[@class="entry-title td-module-title"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//h1[@class="entry-title"]/text()').extract_first(default="").strip()

    def get_author(self, response) -> list:
        authors = response.xpath('//div[@class="td-post-author-name"]/a/text()').extract() or []
        return [a.strip() for a in authors]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//time[@class="entry-date updated td-module-date"]/@datetime').extract_first()
            dt = datetime_helper.fuzzy_parse_timestamp(_time)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//ul[@class='td-tags td-post-small-box clearfix']/li//text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//div[@class="td-post-content tagdiv-type"]/*'
                '|//div[@class="td-post-content tagdiv-type"]/figure/img'
                '|//div[@class="td-post-content tagdiv-type"]/div/figure/noscript/img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag == "div":
                text = ' '.join(tag.xpath("./text()").extract() or []).strip()
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
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
