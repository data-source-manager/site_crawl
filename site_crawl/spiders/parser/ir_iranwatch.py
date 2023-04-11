# -*- coding: utf-8 -*-
# update:(liyun|2023-03-09) -> 板块核对与解析代码覆盖
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class IR_iranwatchParser(BaseParser):
    name = 'ir_iranwatch'

    
    # 站点id
    site_id = "83ff9343-e581-497b-babd-23cb702caee8"
    # 站点名
    site_name = "伊朗观察"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "83ff9343-e581-497b-babd-23cb702caee8", "source_name": "伊朗观察", "direction": "ir", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("606898ee-1a08-4f5b-931f-eb9e153219df", "伊朗实体", "", "政治"),
            ("2d9fa84c-7908-499a-8a11-cbcbf7cdecc2", "伊朗实体/伊朗实体的字母顺序列表", "https://www.iranwatch.org/iranian-entities", "军事"),
            ("271310b3-70a7-4e7e-b751-501a0ce73bab", "伊朗实体/伊朗特色实体", "https://www.iranwatch.org/iranian-entities-featured", "军事"),
            ("7bbce8a5-e76b-4e12-95c4-412cf1a99418", "伊朗实体/最近添加的伊朗实体", "https://www.iranwatch.org/iranian-entities-recent", "军事"),
            ("f66642fe-55a0-4e79-8b3a-c91eb2954942", "伊朗实体/联合国-欧盟制裁统计", "https://www.iranwatch.org/sanctions", "军事"),
            ("df93b324-ee20-4ab2-a98f-b769a9858e90", "图书馆", "", "政治"),
            ("96036b69-5d6b-4efb-b4b1-3dd26349b9d3", "图书馆/个人观点", "https://www.iranwatch.org/authoring-agency/private-viewpoints", "军事"),
            ("3d230429-621b-4499-99d8-eb9e54eddf79", "图书馆/各国政府", "https://www.iranwatch.org/authoring-agency/governments", "军事"),
            ("eeecdf3a-2128-4ca6-88ad-e6e9678777e7", "图书馆/多边组织", "https://www.iranwatch.org/authoring-agency/multilateral-organizations", "军事"),
            ("1e218784-cfed-4d59-8210-d6c16bd3c517", "图书馆/新闻简报", "https://www.iranwatch.org/library/news-briefs", "军事"),
            ("8a033130-186e-4f53-910a-6164858a5e5b", "我们的刊物", "", "政治"),
            ("4a8e7884-fe6f-11ec-a30b-d4619d029786", "我们的刊物/国际执法行动", "https://www.iranwatch.org/our-publications/international-enforcement-actions", "军事"),
            ("38e68295-4ac4-4296-bb81-5e3d20c1beea", "我们的刊物/圆桌会议", "https://www.iranwatch.org/our-publications/roundtables", "军事"),
            ("4a8e77b2-fe6f-11ec-a30b-d4619d029786", "我们的刊物/政策简报", "https://www.iranwatch.org/our-publications/policy-briefs", "军事"),
            ("4a8e7820-fe6f-11ec-a30b-d4619d029786", "我们的刊物/文章和报告", "https://www.iranwatch.org/our-publications/articles-and-reports", "军事"),
            ("4a8e78f2-fe6f-11ec-a30b-d4619d029786", "我们的刊物/时事通讯", "https://www.iranwatch.org/our-publications/newsletters/", "军事"),
            ("b05b672d-eeb1-4baf-86a1-14be9e9aeb42", "我们的刊物/演讲与证词", "https://www.iranwatch.org/our-publications/speeches-and-testimony", "军事"),
            ("40fcc86f-3c72-446c-9384-cc2a0b139fdb", "我们的刊物/访谈和播客", "https://www.iranwatch.org/our-publications/interviews-and-podcasts", "军事"),
            ("97766149-0e87-4aec-8ed2-d53982e95a6b", "武器计划", "", "政治"),
            ("683ca766-d29d-496d-b2d5-1ba096b6a665", "武器计划/化学", "https://www.iranwatch.org/weapon-programs/chemical", "军事"),
            ("6d2618ba-8689-4055-b1dd-2c855fee5317", "武器计划/导弹", "https://www.iranwatch.org/weapon-programs/missile", "军事"),
            ("91e62a97-a4ff-45a3-8c55-f2bc4a6ffc20", "武器计划/核", "https://www.iranwatch.org/weapon-programs/nuclear", "军事"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@id="content"]//span[@class="field-content"]/a/@href'
            '|//div[@class="view-content"]//caption/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//h1[@id="page-title"]/text()').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//span[@property="dc:date"]/@content').extract_first(default="").strip()
            return datetime_helper.parseTimeWithTimeZone(publish_date)
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="field-item even"]/*'
            '|//div[@class="field-items"]//img'
            '|//span[@class="file"]/a'
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
                if img_src == "https://www.iranwatch.org/modules/file/icons/application-pdf.png":
                    continue
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
            # 解析文件附件
            elif tag.root.tag == "a":
                file_src = tag.attrib.get("href")
                if not file_src or not file_src.endswith(".pdf"):
                    continue
                content.append({
                    "type": "file",
                    "src": file_src,
                    "name": tag.attrib.get('title'),
                    "description": None,
                    "md5src": self.get_md5_value(file_src) + ".pdf"
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
