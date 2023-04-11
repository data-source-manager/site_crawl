# update:(liyun|2023-02-16) -> 修正解析代码，过滤src=data:image类别的图片
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class InNaiduNiaParser(BaseParser):
    name = 'naidunia'
    
    # 站点id
    site_id = "0feba444-8a37-4279-b521-077e20718ab3"
    # 站点名
    site_name = "新世界报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "0feba444-8a37-4279-b521-077e20718ab3", "source_name": "新世界报", "direction": "in", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d8550-fe6f-11ec-a30b-d4619d029786", "国外", "https://www.naidunia.com/world", "政治"),
            ("4a8d85c8-fe6f-11ec-a30b-d4619d029786", "国家", "https://www.naidunia.com/national", "政治"),
            ("4a8d8636-fe6f-11ec-a30b-d4619d029786", "最新消息", "https://www.naidunia.com/latest-news?itm_medium=latestnews&itm_source=msite&itm_campaign=navigation", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//ul[@class="topicList"]/li/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        authors = response.xpath('//meta[@itemprop="publisher"]/@content').extract()
        return [a.strip() for a in authors]

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
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
                '//div[@id="bodySummery"]/*'
                '|//div[@id="bodySummery"]//img'
                '|//div[@class="topimgbox"]//img'
        ) or []:
            # 解析段落文本
            if tag.root.tag == "ul" and tag.attrib.get("class") == "tagList":
                break
            elif tag.root.tag in ["p", "span", "div", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                if text.startswith("Font Size"):
                    break
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
            # 解析图像数据
            elif tag.root.tag == "img":
                img_src = tag.attrib.get("srcset", "") or tag.attrib.get("src", "")
                if not img_src or img_src.startswith("data:image"):
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
