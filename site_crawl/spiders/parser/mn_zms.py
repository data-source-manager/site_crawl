# Name: 站点解析器开发
# Date: 2023-03-16
# Author: liyun
# Desc: None


import datetime
import re
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser


###
class MnZmsParser(BaseParser):
    name = 'mn_zms'
    
    # 站点id
    site_id = "3e7bb434-eb22-4e33-a1d6-e6a4125fa20c"
    # 站点名
    site_name = "世纪新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "3e7bb434-eb22-4e33-a1d6-e6a4125fa20c", "source_name": "世纪新闻", "direction": "mn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("28b7c75d-d426-4b07-a7c8-591df8346021", "在世界上", "https://www.zms.mn/as/world", "政治"),
            ("d918caa6-8ff5-49da-b58a-e52040285ee6", "女性领导力", "https://www.zms.mn/as/emegteichuud", "政治"),
            ("a5d5336c-2643-4b86-86e6-94f7934bc32c", "政治", "https://www.zms.mn/as/politics", "政治"),
            ("39c0d0cb-9f69-41df-8d91-370f6d562b89", "社会", "https://www.zms.mn/as/niigem", "政治"),
            ("e1f55d4c-5307-44d2-bd6e-1a135a121256", "蒙古遗产和文化", "https://www.zms.mn/as/tradition", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "3e7bb434-eb22-4e33-a1d6-e6a4125fa20c"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//a[@class="article-item__title"]/@href'
            '|//a[@class="top-feature__title"]/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@name="DC.Publisher"]/@content').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//div[@class="content-meta__left"]/span/span/text()').extract_first(default="").strip()
            if "мин" in publish_date:
                h, m = re.findall(r'(\d+) цаг (\d+) мин', publish_date)[0]
                publish_date = str(datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(hours=-int(h), minutes=-int(m)))
            else:
                publish_date = str(datetime.datetime.strptime(publish_date, "%Y-%m-%d"))
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="content_text"]/*'
            '|//a[@class="uk-inline"]/img'
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
                # img_src = img_src.split("?")[0].split(" ")[0]
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
