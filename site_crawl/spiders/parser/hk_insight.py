# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class HK_insightParser(BaseParser):
    name = 'hk_insight'
    
    # 站点id
    site_id = "160a56a3-fbd5-4e5f-a32e-920a2eca3d4b"
    # 站点名
    site_name = "灼见名家"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "160a56a3-fbd5-4e5f-a32e-920a2eca3d4b", "source_name": "灼见名家", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("40f70c52-7c88-0926-b7c6-f5d87251fe21", "专题", "", "政治"),
            ("4a8df210-fe6f-11ec-a30b-d4619d029786", "专题/两岸关系", "https://www.master-insight.com/tag/%E5%85%A9%E5%B2%B8%E9%97%9C%E4%BF%82/", "政治"),
            ("4a8df288-fe6f-11ec-a30b-d4619d029786", "专题/中美关系", "https://www.master-insight.com/tag/%e4%b8%ad%e7%be%8e%e9%97%9c%e4%bf%82%e5%b0%88%e9%a1%8c/", "政治"),
            ("4a8df2f6-fe6f-11ec-a30b-d4619d029786", "专题/武统", "https://www.master-insight.com/tag/%e6%ad%a6%e7%b5%b1/", "政治"),
            ("4a8df1a2-fe6f-11ec-a30b-d4619d029786", "政局", "https://www.master-insight.com/category/theme/%E6%94%BF%E5%B1%80/", "政治"),
            ("296409a0-2e20-4301-b301-9e27be67bda6", "政局/中国", "https://www.master-insight.com/category/theme/%e6%94%bf%e5%b1%80/%e6%94%bf%e5%b1%80-%e4%b8%ad%e5%9c%8b/", "政治"),
            ("a55c59db-28bd-41ae-bf5f-c6acff3df97b", "政局/台湾", "https://www.master-insight.com/category/theme/%e6%94%bf%e5%b1%80/%e5%8f%b0%e7%81%a3/", "政治"),
            ("9b423dbc-2030-42fb-a1f2-29957fccb3f7", "政局/国际", "https://www.master-insight.com/category/theme/%e6%94%bf%e5%b1%80/%e5%9c%8b%e9%9a%9b/", "政治"),
            ("586beaa0-e1bf-4af0-ba9a-b2b07b022104", "政局/香港", "https://www.master-insight.com/category/theme/%e6%94%bf%e5%b1%80/%e9%a6%99%e6%b8%af/", "政治"),
            ("ce23f755-cd22-1348-ba78-3d3a88499ae1", "财经", "", "政治"),
            ("f8f4a9a2-d805-49e0-941e-b07577eda043", "财经/地产", "https://www.master-insight.com/category/theme/%e8%b2%a1%e7%b6%93/%e5%9c%b0%e7%94%a2/", "经济"),
            ("25d90449-d752-4024-a506-7bcd81202dfc", "财经/投资", "https://www.master-insight.com/category/theme/%e8%b2%a1%e7%b6%93/%e6%8a%95%e8%b3%87/", "经济"),
            ("84f9c690-c80a-4036-93d7-bdb0e8220fbc", "财经/金融", "https://www.master-insight.com/category/theme/%e8%b2%a1%e7%b6%93/%e9%87%91%e8%9e%8d/", "经济"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "160a56a3-fbd5-4e5f-a32e-920a2eca3d4b"
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//h3[@class='jeg_post_title']/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='jeg_post_title']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_a = response.xpath("//div[@class='jeg_meta_author']/a[@rel='author']/text()").get()
        if author_a and "編輯部" not in author_a:
            authors.append(author_a.strip())
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='jeg_meta_date']/a/text()").get()

        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@class='jeg_inner_content']/div[@class='jeg_post_tags']/a/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@class='content-inner ']/*"
            "|//div[@data-type='youtube']"
            '|//div[@class="jeg_featured featured_image"]//img'
            # '|//div[@class="content-inner "]/p/a/noscript/img'
            '|//div[@class="content-inner "]/p//img'
        )
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    # if news_tag.xpath(".//img"):
                    #     img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src", des_xpath=".//img/@alt")
                    #     if img_src:
                    #         content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag == 'img':
                    # 解析图像字段
                    img_url = urljoin(response.url, news_tag.attrib.get('data-src') or news_tag.attrib.get('src'))
                    suffix = img_url.split(".")[-1].lower()
                    if suffix in ["jpg", "png", "jpeg"]:
                        content.append({
                            "type": "image",
                            "name": None,
                            "md5src": self.get_md5_value(img_url) + f'.{suffix}',
                            "description": news_tag.attrib.get("alt", ""),
                            "src": img_url
                        })
                elif news_tag.root.tag == 'div' and news_tag.root.get("data-type") == "youtube":
                    video_src = self.parse_media(response, news_tag)
                    if video_src:
                        content.append(video_src)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url,
                            news_tag.xpath("./@data-src").extract_first())
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(video_src) + ".mp4"
        }
        return video_dic

    def get_like_count(self, response) -> int:
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
