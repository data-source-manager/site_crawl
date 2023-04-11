# Name: 站点解析器开发
# Date: 2023-03-16
# Author: liyun
# Desc: None


from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser


class MnMontsaMeParser(BaseParser):
    name = 'mn_montsame'
    
    # 站点id
    site_id = "637e0ed4-2b9c-4e7f-8e29-2692372fb125"
    # 站点名
    site_name = "蒙萨姆通讯社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "637e0ed4-2b9c-4e7f-8e29-2692372fb125", "source_name": "蒙萨姆通讯社", "direction": "mn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("96d712cd-8c34-47de-91c1-8528907c68ec", "关于蒙古", "https://montsame.mn/en/more/301", "政治"),
            ("806c1fb4-35d9-4407-a7f1-de8bef8aafad", "政治", "https://montsame.mn/en/more/302", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "637e0ed4-2b9c-4e7f-8e29-2692372fb125"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="row no-gutters"]/div/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//div[@class="author my-2 align-middle d-print-none"]/div/div/a/span/text()').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//span[@class="stat"]/text()').extract_first(default="").strip()
            # publish_date = datetime_helper.parseTimeWithOutTimeZone(
            #     datetime.strptime(publish_date, "%Y-%m-%d %H:%M:%s")
            # )
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="news-body my-3 content-en"]/*'
            '|//div[@class="news-body my-3 content-en"]//img'
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
