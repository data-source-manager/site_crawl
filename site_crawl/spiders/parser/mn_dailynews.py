# Name: 站点解析器开发
# Date: 2023-03-16
# Author: liyun
# Desc: None


from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


###
class MnDailynewsParser(BaseParser):
    name = 'mn_dailynews'
    
    # 站点id
    site_id = "1ce38bce-ed96-43b3-91c0-8ced4cf51516"
    # 站点名
    site_name = "每日新闻MN"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "1ce38bce-ed96-43b3-91c0-8ced4cf51516", "source_name": "每日新闻MN", "direction": "mn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e5d32a9d-5fb2-4ad9-a394-6e1a8a37ff67", "世界", "http://dailynews.mn/?cat=8", "政治"),
            ("a2f80b90-ef9a-4b74-9b43-40469fe01e69", "政治", "http://dailynews.mn/?cat=5", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "1ce38bce-ed96-43b3-91c0-8ced4cf51516"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h3[@class="jeg_post_title"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return (
            response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()
            or
            response.xpath('//meta[@name="twitter:title"]/@content').extract_first(default="").strip()
        ) 

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//div[@class="jeg_meta_author"]/span/a/text()').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//meta[@property="article:published_time"]/@content').extract_first(default="").strip()
            publish_date = datetime_helper.parseTimeWithTimeZone(publish_date)
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="desc_contents"]/*'
            '|//div[@class="content-inner "]/*'
            '|//div[@class="desc_contents"]//img'
            '|//div[@class="content-inner "]//img'
            '|//div[@class="thumbnail-container animate-lazy"]/img'
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
                img_src = tag.attrib.get("data-src", "") or tag.attrib.get("src", "")
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
