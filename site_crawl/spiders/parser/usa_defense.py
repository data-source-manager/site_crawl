# -*- coding: utf-8 -*-
# update:(liyun|2023-03-06) -> 板块核对与解析代码覆盖
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaDefenseParser(BaseParser):
    name = 'defense'
    
    # 站点id
    site_id = "50ed1049-8a3a-4e70-bb42-302ba793c3ab"
    # 站点名
    site_name = "美国国防部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "50ed1049-8a3a-4e70-bb42-302ba793c3ab", "source_name": "美国国防部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("5c952984-92cb-5725-6ef5-11e114990acc", "专题", "", "政治"),
            ("4a8bf87a-fe6f-11ec-a30b-d4619d029786", "专题/北约", "https://www.defense.gov/Spotlights/Nato/", "政治"),
            ("4a8bf80c-fe6f-11ec-a30b-d4619d029786", "消息", "https://www.defense.gov/News/", "政治"),
            ("448948ad-af42-4e51-9dd1-cd30d3277d85", "消息/冲压产品", "https://www.defense.gov/News/Press-Products/", "政治"),
            ("e700b190-7607-11ed-ad4d-d4619d029786", "消息/新闻报道", "https://www.defense.gov/News/News-Stories/", "政治"),
            ("662666a5-bb1d-4633-97e4-1a9f5f2e25e5", "消息/来自服务", "https://www.defense.gov/News/From-the-Services/", "政治"),
            ("4d8818c2-332e-4a54-bd66-9d0254a0bb52", "消息/特征", "https://www.defense.gov/News/Feature-Stories/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//listing-with-preview/@article-url'
            '|//listing-dashboard-with-preview/@article-url'
        ).extract() or []
        for news_url in list(set(news_urls)):
            news_url = urljoin(response.url, news_url)
            if news_url.startswith('https://www.defense.gov/') or news_url.startswith('http://www.defense.gov/'):
                yield news_url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//span[@class="author-block"]/a/text()').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//span[@class="date"]/text()').extract_first()
            _time = str(datetime_helper.fuzzy_parse_datetime(_time))
            return _time
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return [a.strip() for a in response.xpath('//div[@class="tags"]/a/text()').extract() or []]

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="body"]/*'
            '|//div[@class="image"]/img'
            '|//div[@class="image-wrapper"]/img'
            '|//div[@class="image-wrapper video video-wrap-container"]/video'
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
            # 解析视频
            elif tag.root.tag == "video":
                video_src = tag.attrib.get("src", "")
                if not video_src:
                    continue
                video_src = video_src.split("?")[0].split(" ")[0]
                video_src = urljoin(response.url, video_src)
                suffix = video_src.split(".")[-1].lower()
                if (not video_src.startswith('http')) or (suffix not in ["mp4"]):
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
        return "en"

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
