import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaC4isrnetParser(BaseParser):
    name = 'usa_c4isrnet'
    
    # 站点id
    site_id = "82707da4-95b3-40a6-98dd-9a5d0d74052b"
    # 站点名
    site_name = "第五域"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "82707da4-95b3-40a6-98dd-9a5d0d74052b", "source_name": "第五域", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("563e0ee0-591e-4db0-b5d0-d2027516ed81", "战地科技", "https://www.c4isrnet.com/battlefield-tech/", "军事"),
            ("763c912c-8bba-4e5f-b938-79010e021d7e", "战地科技/JADC2和通信", "https://www.c4isrnet.com/battlefield-tech/c2-comms/", "军事"),
            ("a4d59e3e-5d71-fe1c-fd2e-70916a17478a", "战地科技/信息技术", "", "政治"),
            ("9e781983-3487-4dfd-a213-eda1e25eaac0", "战地科技/信息技术/网络", "https://www.c4isrnet.com/battlefield-tech/it-networks/", "军事"),
            ("4092078b-2e8f-4f56-a571-879b7585dd1f", "战地科技/空间", "https://www.c4isrnet.com/battlefield-tech/space/", "军事"),
            ("991793eb-56aa-43a7-b7ff-c9720431078a", "无人", "https://www.c4isrnet.com/unmanned/", "军事"),
            ("d6111641-20fa-4a0f-b501-a4bf92a85b3c", "无人/无人机技术", "https://www.c4isrnet.com/unmanned/robotics/", "军事"),
            ("5bef30c0-6e47-4517-85ef-0e62b9edd03a", "电子战", "https://www.c4isrnet.com/electronic-warfare/", "军事"),
            ("7e4c4543-e1ba-496a-b4d3-d703ba1cfdad", "网络", "https://www.c4isrnet.com/cyber/", "军事"),
            ("1ab3c24f-8c43-45fc-8643-a7d6fb9c7230", "行业", "https://www.c4isrnet.com/industry/", "军事"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//main//h5/a/@href|//main//h6/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@property="og:author"]/@content').extract() or []]

    def get_pub_time(self, response) -> str:
        _time = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if _time:
            pub_time = datetime_helper.fuzzy_parse_timestamp(_time)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        # return [a.strip() for a in response.xpath('').extract() or []]
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//section/div/article/*'
                '|//section/div[1]//picture/img'
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
