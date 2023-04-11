# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    站点解析模版
"""


class HkHk01Parser(BaseParser):
    name = 'hk01'
    
    # 站点id
    site_id = "32314e3c-4a56-450f-a036-414753e8484b"
    # 站点名
    site_name = "香港01"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "32314e3c-4a56-450f-a036-414753e8484b", "source_name": "香港01", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("6453c946-ba3f-3006-b8e4-1afaec7469e1", "中国", "", "政治"),
            ("635e4738-381c-4b82-b831-608f46e370b8", "中国/中国观察", "https://www.hk01.com/channel/458/%E4%B8%AD%E5%9C%8B%E8%A7%80%E5%AF%9F", "政治"),
            ("5fa0033f-2ed3-4f10-bbc1-07fdc4691eb6", "中国/即时中国", "https://www.hk01.com/channel/364/%E5%8D%B3%E6%99%82%E4%B8%AD%E5%9C%8B", "政治"),
            ("19b34558-2683-499d-b0ec-2ab72b770e36", "中国/即时国际", "https://www.hk01.com/channel/19/%E5%8D%B3%E6%99%82%E5%9C%8B%E9%9A%9B", "政治"),
            ("4a8d96f8-fe6f-11ec-a30b-d4619d029786", "中国/台湾新闻", "https://www.hk01.com/channel/367/%E5%8F%B0%E7%81%A3%E6%96%B0%E8%81%9E", "政治"),
            ("4a8d9626-fe6f-11ec-a30b-d4619d029786", "国际", "", "政治"),
            ("13f19617-d5dd-4d2f-a23d-ef077e559cf8", "国际/即时国际", "https://www.hk01.com/channel/19/%E5%8D%B3%E6%99%82%E5%9C%8B%E9%9A%9B", "政治"),
            ("ffccaf23-6388-466a-b886-3006a91c1764", "国际/国际分析", "https://www.hk01.com/channel/407/%E5%9C%8B%E9%9A%9B%E5%88%86%E6%9E%90", "政治"),
            ("138ea944-2518-36c8-86c5-dc5ddd18eb81", "港闻", "", "政治"),
            ("4a8d94f0-fe6f-11ec-a30b-d4619d029786", "港闻/政情", "https://www.hk01.com/channel/310/%E6%94%BF%E6%83%85", "政治"),
            ("c4ac9b3d-5eb4-4274-80e3-19e0e3a8365d", "港闻/深度", "https://www.hk01.com/channel/413/%E6%B7%B1%E5%BA%A6%E5%A0%B1%E9%81%93", "政治"),
            ("9b34539b-3db0-43d8-ad3f-71f2968012c6", "港闻/香港经济", "https://www.hk01.com/channel/403/%E9%A6%99%E6%B8%AF%E7%B6%93%E6%BF%9F", "政治"),
            ("a47cdc4e-aef5-1b2d-cdd4-2967980d87e3", "经济", "", "政治"),
            ("21752a80-08ab-4930-a0fb-9c8844935ed1", "经济/财经快讯", "https://www.hk01.com/channel/396/%E8%B2%A1%E7%B6%93%E5%BF%AB%E8%A8%8A", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "32314e3c-4a56-450f-a036-414753e8484b"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div//a[contains(@data-testid,"contentCard-title")]/@href|'
                                   '//a[contains(@data-testid,"common-contentCard-title")]/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@id="articleTitle"]/text()|//meta[@property="og:title"]/@content').extract_first(
            default="")
        return title.strip().replace('\u3000', '') if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = "".join(response.xpath('//meta[@name="keywords"]/@content').extract())
        if tags:
            if "," in tags:
                tags = tags.split(",")

            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        head_img = response.xpath(
            '//meta[@property="og:image"]/@content|//article//div[@class="f1oxu5xj"]/img').extract_first()
        if head_img:
            img_dict = {"type": "image",
                        "name": "",
                        "md5src": self.get_md5_value(head_img) + '.jpg',
                        "description": "",
                        "src": head_img
                        }
            content.append(img_dict)

        news_tags = response.xpath('//article[@id="article-content-section"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)

                if news_tag.root.tag == "div":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('').extract() or ""

        new_cons = []

        if cons:
            for con in cons:
                if con.strip():
                    new_cons.append({'data': "".join(con).strip(), 'type': "text"})
        return new_cons

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip().replace('\u3000', '')
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            if img.startswith("data:image/gif;base64"):
                return {}
            img_url = urljoin(response.url, img)

            des = "".join(news_tag.xpath('.//figcaption//text()').extract()).strip()
            if not des:
                des = news_tag.xpath(".//img/@alt").extract()

            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": des,
                   "src": img_url
                   }
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath(".//@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.attrib.get('title'),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag, media_type):
        videoUrl = news_tag.xpath("./@src").extract_first()
        suffix = f".{media_type}"

        video_dic = {}

        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }

            if suffix == ".mp3":
                video_dic["type"] = "audio"
            elif suffix == ".mp4":
                video_dic["type"] = "video"

        return video_dic

    def get_like_count(self, response) -> int:
        like_count = response.xpath('//div[contains(@class,"button__total_count")]/text()').extract_first()
        if like_count:
            return int(like_count.strip())
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
