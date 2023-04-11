# -*- coding: utf-8 -*-
# update:(liyun|2023-03-14) -> 板块核对与解析代码覆盖
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TW_hxnewsParser(BaseParser):
    name = 'tw_hxnews'

    
    # 站点id
    site_id = "56a0f388-ecbc-4e3a-affb-6c315cf4e274"
    # 站点名
    site_name = "台海新闻网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "56a0f388-ecbc-4e3a-affb-6c315cf4e274", "source_name": "台海新闻网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("df9aec73-41c3-4e6c-9c22-2a63b1ece3c1", "三明新闻", "http://www.hxnews.com/news/fj/sm/", "社会"),
            ("b6180fb8-774f-4f71-b448-c88f2c12d639", "南平新闻", "http://www.hxnews.com/news/fj/np/", "社会"),
            ("d9004428-ec5b-4cfb-841d-f329aa72d2b3", "厦门新闻", "http://www.hxnews.com/news/fj/mn/xm/", "社会"),
            ("4a8ea462-fe6f-11ec-a30b-d4619d029786", "台湾选举", "http://www.hxnews.com/news/la/twxj/", "政治"),
            ("4a8ea52a-fe6f-11ec-a30b-d4619d029786", "国内时政", "http://www.hxnews.com/news/gn/szxw/", "政治"),
            ("4a8ea4f8-fe6f-11ec-a30b-d4619d029786", "国际军事", "http://www.hxnews.com/news/gj/jsxw/", "政治"),
            ("4a8ea4c6-fe6f-11ec-a30b-d4619d029786", "国际政治", "http://www.hxnews.com/news/gj/gjzz/", "政治"),
            ("4a8ea494-fe6f-11ec-a30b-d4619d029786", "国际新闻", "http://www.hxnews.com/news/gj/gjxw/", "政治"),
            ("6b46a9ca-0ee3-4833-b672-ce0791fc7ed8", "宁德新闻", "http://www.hxnews.com/news/fj/nd/", "社会"),
            ("7ad48a84-86db-41a6-b636-f381af430590", "平潭新闻", "http://www.hxnews.com/news/fj/pingtan/", "社会"),
            ("4a8ea430-fe6f-11ec-a30b-d4619d029786", "海峡两岸", "http://www.hxnews.com/news/la/", "政治"),
            ("68d8bcab-72cd-4318-9ec5-23305af44c80", "福州新闻", "http://www.hxnews.com/news/fj/fz/", "社会"),
            ("0d69b3ae-7f6d-4570-b1dd-f5a3c21be92c", "福建新闻", "http://www.hxnews.com/news/fj/fj/", "社会"),
            ("ca893eda-a7da-4742-bb63-5f0b339d243f", "莆田新闻", "http://www.hxnews.com/news/fj/pt/", "社会"),
            ("3cc62cd1-24d8-4a59-b983-d615dea98626", "闽南新闻", "http://www.hxnews.com/news/fj/mn/", "社会"),
            ("5aa5c3dd-77e6-4eb3-b35f-91b4657d0d49", "龙岩新闻", "http://www.hxnews.com/news/fj/ly/", "社会"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//ul[@class="newlistbox"]/li/div/h3/a[last()]/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        try:
            author = response.xpath('//p[@class="article-editor"]/text()').extract_first(default="").strip()
            author = author.split("：")[1].strip()
            return [author]
        except:
            return []

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//meta[@property="og:release_date"]/@content').extract_first(default="").strip()
            publish_date = datetime_helper.parseTimeWithOutTimeZone(
                datetime.strptime(publish_date, "%Y-%m-%d %H:%M"),
                site_name="台海新闻网"
            )
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return [a.strip() for a in response.xpath('//div[@class="keywords"]/a/text()').extract() or []]

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="article article_16 article-content fontSizeSmall"]/*'
            '|//div[@class="article article_16 article-content fontSizeSmall"]//img'
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
