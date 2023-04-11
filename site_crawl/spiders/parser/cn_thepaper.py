# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    站点解析模版
"""


class CnThepaperParser(BaseParser):
    name = 'thepaper'
    
    # 站点id
    site_id = "dbdc4fe5-aa74-47ed-8ecc-401e357b35f0"
    # 站点名
    site_name = "澎湃新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "dbdc4fe5-aa74-47ed-8ecc-401e357b35f0", "source_name": "澎湃新闻", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("b0c2130a-7218-11ed-a54c-d4619d029786", "国际", "https://www.thepaper.cn/list_25429", "政治"),
            ("b0c2144a-7218-11ed-a54c-d4619d029786", "时事", "https://www.thepaper.cn/channel_25950", "政治"),
            ("b0c213dc-7218-11ed-a54c-d4619d029786", "要闻", "https://www.thepaper.cn/", "政治"),
            ("b0c21378-7218-11ed-a54c-d4619d029786", "评论", "https://www.thepaper.cn/channel_-24", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="small_toplink__GmZhY"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                url = urljoin(response.url, news_url)
                if "www.thepaper.cn" not in url:
                    continue
                yield url

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="index_title__B8mhI"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath(
            '//div[@class="index_left__LfzyH"]//div[@class="ant-space-item"]/span/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@class="index_tags__Mo75P"]/a/span/text()').extract()
        if tags:
            for tag in tags:
                if tag.replace("#", "").strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        video_url = re.findall('http\S+.mp4', response.text)
        if video_url:
            video_dic = {
                "type": "mp4",
                "src": video_url[0],
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_url[0]) + ".mp4"
            }
            content.append(video_dic)

        news_tags = response.xpath('//div[@class="index_cententWrap__Jv8jK"]/*|'
                                   '//p[@class="header_desc__OlmEB"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)

                if news_tag.root.tag == "img":
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
            oneCons = "".join(cons).strip()
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//@src|.//img/@src').extract_first()
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
