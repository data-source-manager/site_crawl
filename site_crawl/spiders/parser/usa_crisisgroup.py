# update:(liyun|2023-02-16) -> 板块核对与解析代码修正
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaCrisisgroupParser(BaseParser):
    name = 'crisisgroup'
    # 站点id
    site_id = "782540c8-201b-4df6-b011-2fc209f785e9"
    # 站点名
    site_name = "国际危机集团"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "782540c8-201b-4df6-b011-2fc209f785e9", "source_name": "国际危机集团", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("48a6c135-997c-449b-9648-f7c7a5cee2e8", "中东和北非", "https://www.crisisgroup.org/middle-east-north-africa", "政治"),
            ("3d8991f9-298f-455d-8780-9c87e17e10a0", "亚洲", "", "政治"),
            ("848b02d5-6f73-4b0a-9702-2847678f67ca", "亚洲/中国", "https://www.crisisgroup.org/asia/north-east-asia/china", "政治"),
            ("91cc3152-e38c-4719-81a2-1868368c7b5b", "亚洲/台湾海峡", "https://www.crisisgroup.org/asia/north-east-asia/taiwan-strait", "政治"),
            ("7e623dea-5f89-44c0-9d61-bd3daac0cc14", "我们的影响", "https://www.crisisgroup.org/our-impact", "政治"),
            ("4a8e27f8-fe6f-11ec-a30b-d4619d029786", "报告", "https://www.crisisgroup.org/latest-updates/reports-and-briefings", "政治"),
            ("6b11515c-b479-4678-b8b3-9aa84bbfefe8", "拉丁美洲和加勒比地区", "https://www.crisisgroup.org/latin-america-caribbean", "政治"),
            ("4a8e282a-fe6f-11ec-a30b-d4619d029786", "播客", "https://www.crisisgroup.org/latest-updates/podcast", "政治"),
            ("adeef09c-415c-4b94-a544-593652b63a63", "档案", "https://www.crisisgroup.org/latest-updates", "政治"),
            ("00e04532-6212-4517-8216-b22b959dbfb3", "欧洲和中亚", "https://www.crisisgroup.org/europe-central-asia", "政治"),
            ("a85bec58-97df-46eb-9b96-e7faf333919d", "美国", "https://www.crisisgroup.org/united-states", "政治"),
            ("9a6867f5-8db9-4e33-a6b5-477aaab0efd3", "视频和摄影", "", "政治"),
            ("2442ef6a-f09b-437a-b564-3e43bd5b4669", "视频和摄影/摄影", "https://www.crisisgroup.org/photography", "政治"),
            ("475bb42d-4e9b-4d88-98cd-beae3350a84e", "视频和摄影/视频", "https://www.crisisgroup.org/videos", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="s-component o-container o-container--cols1 o-container--cols1-r"]//h4/a/@href'
            '|//h4[@class="c-news-listing__title"]/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            news_url = urljoin(response.url, news_url)
            if not news_url.startswith("https://www.crisisgroup.org/who-we-are/people/"):
                yield news_url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        # return [a.strip() for a in response.xpath('//meta[@name="DC.Publisher"]/@content').extract() or []]
        return []

    def get_pub_time(self, response) -> str:
        _time = response.xpath('//meta[@property="article:modified_time"]/@content').extract_first()
        if _time:
            pub_time = datetime_helper.fuzzy_parse_timestamp(_time)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        # return [a.strip() for a in response.xpath('').extract() or []]
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析图片
        img_src = response.xpath('//meta[@property="og:image"]/@content').extract_first(default="").strip()
        suffix = img_src.split("?")[0].split(".")[-1].lower()
        if img_src:
            content.append({
                "type": "image",
                "src": img_src,
                "name": "",
                "md5src": self.get_md5_value(img_src) + f'.{suffix}',
                "description": "",
            })
        # 解析正文数据
        for tag in response.xpath(
                '//div[@class="word-wrap"]/p'
                '|//div[@class="s-article__body u-pos-relative"]/div/*'
                '|//div[@class="o-image o-image--cover"]/img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h1", "h2", "h3", "h4"]:
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
        return "zh-cn"

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
