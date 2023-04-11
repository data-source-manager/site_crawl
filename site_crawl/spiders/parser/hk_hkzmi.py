import re
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser


class HkHkzmiParser(BaseParser):
    name = 'hkzmi'
    
    # 站点id
    site_id = "66531851-a5b3-4c1e-882a-37ab677daafb"
    # 站点名
    site_name = "香港智明研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "66531851-a5b3-4c1e-882a-37ab677daafb", "source_name": "香港智明研究所", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d9a22-fe6f-11ec-a30b-d4619d029786", "亚太局势", "", "政治"),
            ("f44429ea-7148-4fc4-b1e8-878ead882b50", "亚太局势/时事评论", "https://www.hkzmi.com/apac/comments/?q=/apac/", "政治"),
            ("4a8d9a90-fe6f-11ec-a30b-d4619d029786", "台港政经", "", "政治"),
            ("fa1c546f-5189-45dc-ac25-e1b01ad45c29", "台港政经/时事评论", "https://www.hkzmi.com/twhk/comments/?q=/twhk/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id='66531851-a5b3-4c1e-882a-37ab677daafb'
    def parse_list(self, response) -> list:
        news_urls = response.xpath('//ul[@class="article-list"]//a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//div[@class="post-title"]/a/text()').extract_first(default="").strip()

    def get_author(self, response) -> list:
        try:
            author = re.search(r"【文/(\w+)】", response.xpath('//div[@class="post-entry"]/p[2]/text()').extract_first(
                default="")).groups()[0].strip()
            return [author]
        except:
            return []

    def get_pub_time(self, response) -> str:
        try:
            y, m, d = re.search(r'(\d+)年(\d+)月(\d+)日',
                                response.xpath('//div[@class="post-entry"]/p[2]/a/text()').extract_first(
                                    default="")).groups()
            m = "0" + m if len(m) == 1 else m
            d = "0" + d if len(d) == 1 else d
            return f'{y}-{m}-{d} 00:00:00'
        except:
            # import traceback
            # print(traceback.format_exc())
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        # return [a.strip() for a in response.xpath('').extract() or []]
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//div[@class="post-entry"]/*'
                '|//div[@class="post-entry"]//img'
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
                    "description": None,
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
