import re
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser


class HkSavantaSParser(BaseParser):
    name = 'hk_savantas'
    
    # 站点id
    site_id = "c02614b9-2fab-4408-adbe-bd5667e48621"
    # 站点名
    site_name = "汇贤智库"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c02614b9-2fab-4408-adbe-bd5667e48621", "source_name": "汇贤智库", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("574c7f97-bd5a-3a30-a131-cd5625cc0d29", "最新动态", "", "政治"),
            ("1c3f47a3-bfaf-44a2-abbd-7dc4a8d597b1", "最新动态/新闻稿", "https://www.savantas.org/news.php?pid=5&id=20", "其他"),
            ("e9930c16-3c88-4a78-9af3-75bdaf78efbc", "最新动态/最新消息", "https://www.savantas.org/news.php?pid=5&id=19", "其他"),
            ("f0b53aad-1c1c-4838-a87b-98e7fcf6ec0f", "最新动态/电子快讯", "https://www.savantas.org/news.php?pid=5&id=21", "其他"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = 'c02614b9-2fab-4408-adbe-bd5667e48621'

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="cntw activelist"]//h1/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//h1[@class="actitph1"]/text()').extract_first(default="").strip()

    def get_author(self, response) -> list:
        # return [a.strip() for a in response.xpath('//meta[@name="DC.Publisher"]/@content').extract() or []]
        return []

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//p[@class="datep"]/text()').extract_first(default="")
            y, m, d = re.findall(r'\d+', _time)
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
                '//div[@class="actext"]/*'
                '|//div[@class="actext"]//img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4", "div"]:
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
