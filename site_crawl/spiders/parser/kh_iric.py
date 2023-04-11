# update:(liyun:2023-03-07) -> 新增板块与解析代码覆盖
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class KhIrIcParser(BaseParser):
    name = 'iric'
    
    # 站点id
    site_id = "02635630-e104-42e1-8e48-accabebba0e8"
    # 站点名
    site_name = "柬埔寨王家学院国际关系研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "02635630-e104-42e1-8e48-accabebba0e8", "source_name": "柬埔寨王家学院国际关系研究所", "direction": "kn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("33e42f09-7458-494d-90e1-10bead8f0446", "乌尔雷瑟奇斯", "http://iric.gov.kh/category/research/", "其他"),
            ("1f528cf7-7c04-458c-9f35-28e88684b08d", "总干事致辞", "http://iric.gov.kh/category/message/", "政治"),
            ("4a8f5a9c-fe6f-11ec-a30b-d4619d029786", "新闻", "http://iric.gov.kh/category/news/", "政治"),
            ("ad56c661-12dc-4888-829c-4cd7af92741b", "柬埔寨国际关系研究所", "http://iric.gov.kh/category/about-us/", "政治"),
            ("b26188a2-0ef4-4d12-a7c0-9898856d0019", "科门塔里斯", "http://iric.gov.kh/category/commentaries/", "其他"),
            ("c5a14c25-bda8-4fea-ab09-3626a88b4684", "视频", "http://iric.gov.kh/category/video/", "其他"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h2[@class="entry-title"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath(
            '//h1[@class="entry-title"]/text()'
            '|//div[@class="site-branding clearfix"]/h2/text()'
        ).extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//time/@datetime').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="entry-content clearfix"]/*'
            '|//div[@class="entry-content clearfix"]//img'
            '|//div[@class="entry-content clearfix"]//iframe'
            '|//div[@id="logo"]/*'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                if tag.xpath(".//script"):
                    continue
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
            elif tag.root.tag == "iframe":
                # 解析视频
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
