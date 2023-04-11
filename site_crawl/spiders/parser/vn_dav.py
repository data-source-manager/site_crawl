# -*- coding: utf-8 -*-
# update:(liyun|2023-02-02) -> 板块核对与解析代码修正
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class VnDavParser(BaseParser):
    name = 'vn_dav'
    
    # 站点id
    site_id = "0d5d1686-3cc1-40cb-a85a-1e63957abcf1"
    # 站点名
    site_name = "越南外交学院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "0d5d1686-3cc1-40cb-a85a-1e63957abcf1", "source_name": "越南外交学院", "direction": "vn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("09e2ba39-6494-4070-a1c2-c4ba77da1d42", "国际的", "", "政治"),
            ("00030a44-0a4e-43de-87f0-063cf4e3c4df", "国际的/促进国际合作", "https://dav.edu.vn/hop-tac-quoc-te-boi-duong/", "政治"),
            ("a8637230-0d2d-48bb-b98c-ed8017e2f861", "国际的/国际合作研究", "https://dav.edu.vn/hop-tac-quoc-te-nghien-cuu/", "政治"),
            ("9ac5b366-fbed-436b-8fad-ff34de8f8c6e", "国际的/国际培训合作", "https://dav.edu.vn/hoc-vien-ngoai-giao-ky-bien-ban-ghi-nho-hop-tac-voi-vien-hoa-binh-my-usip/", "政治"),
            ("80ec4733-7231-47d9-b614-bd0c55eb2c40", "国际的/外交使团活动", "https://dav.edu.vn/hoat-dong-ngoai-giao-doan/", "政治"),
            ("fa9ff39e-3e38-4d7f-b063-52cd264043fa", "国际的/频道2外交活动", "https://dav.edu.vn/mang-luoi-ngoai-giao-kenh-2/", "政治"),
            ("3231afee-e34c-4349-b46e-9e9c81e638b5", "消息", "", "政治"),
            ("b4a4ab8c-7514-4508-a51e-983a9342f91e", "消息/专题新闻", "https://dav.edu.vn/tin-tuc-noi-bat/", "政治"),
            ("947c9bd8-af76-46df-a8f3-96ca4ca42d1d", "消息/研讨会-会谈", "https://dav.edu.vn/tin-tuc-hoi-thao-toa-dam/", "政治"),
            ("4a8dfb2a-fe6f-11ec-a30b-d4619d029786", "研究", "", "政治"),
            ("6b7f7f22-1e39-442f-99e0-930dc6b064dd", "研究/刊物", "https://dav.edu.vn/an-pham-nghien-cuu/", "政治"),
            ("df8f93a6-9eb3-42f2-8bfd-490cf1e5db5b", "研究/活动-工作坊-会谈", "https://dav.edu.vn/su-kien-hoi-thao-toa-dam/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = '0d5d1686-3cc1-40cb-a85a-1e63957abcf1'

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//main//figure[@class="story__thumb"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        _time = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
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
                '//article[@class="detail-wrap"]/header/*'
                '|//article[@class="detail-wrap"]/div[@class="detail__content"]/*'
                '|//article[@class="detail-wrap"]/div[@class="detail__content"]//img'
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
