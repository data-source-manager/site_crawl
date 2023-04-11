# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class VN_thanhnienParser(BaseParser):
    name = 'vn_thanhnien'
    
    # 站点id
    site_id = "54396803-e15e-4231-8b96-09036bf561af"
    # 站点名
    site_name = "越南青年报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "54396803-e15e-4231-8b96-09036bf561af", "source_name": "越南青年报", "direction": "vn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("36bdb649-3def-3b88-9d94-30477818c1df", "世界", "", "政治"),
            ("e19bc1d3-2817-4c9f-be3a-73b51584eeff", "世界/军队", "https://thanhnien.vn/the-gioi/quan-su/", "政治"),
            ("582b8e88-7cd6-448d-a088-a6edd45f9825", "世界/看法", "https://thanhnien.vn/the-gioi/goc-nhin/", "政治"),
            ("1e698f47-e133-4df4-9473-f5b4d2adc579", "世界/经济", "https://thanhnien.vn/the-gioi/kinh-te-the-gioi/", "政治"),
            ("8e489da1-3bb8-4ad4-b55e-433c2d20b599", "消息", "", "政治"),
            ("a1f629c7-06bc-4d2f-b920-fff27684c774", "消息/国际", "https://thanhnien.vn/thoi-su/quoc-phong/", "政治"),
            ("2c3a1883-db99-4e9a-8311-50a2c56ce587", "消息/政治", "https://thanhnien.vn/thoi-su/chinh-tri/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="l-content"]//a[@class="story__thumb"]/@href|'
                                   '//h3[@class="box-title-text"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "post1524495" in response.url:
            title_ = response.xpath('//title/text()').extract_first(default="")
            title = re.findall('(.*) \(23', title_)[0]
            return title.strip() if title else ""
        else:
            title = response.xpath('//h1[@class="details__headline cms-title"]/text()|'
                                   '//meta[@property="og:title"]/@content').extract_first(default="")
            return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

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

        tags = response.xpath('//div[@class="details__tags"]/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="clearfix cms-video"]|//div[@id="storybox"]//div[@id="abody"]/*|'
                                   '//div[@id="storybox"]/div[@class="l-content"][1]//img|'
                                   '//div[@class="section-content"]/*|//div[@data-role="content"]/*|'
                                   '//div[@data-role="content"]//img')
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

                if news_tag.root.tag == "div":
                    con_file = self.parse_media(response, news_tag, media_type="video")
                    if con_file:
                        content.append(con_file)

                if news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip().replace('\n', '').replace('\xa0', '')
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@src').extract_first()
        if img.startswith("data:image/"):
            return {}
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//figcaption//text()').extract()).strip(),
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
        videoUrl = news_tag.xpath("./@data-video-src").extract_first()
        if media_type == "video":
            suffix = ".mp4"
        else:
            suffix = ".mp3"
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }
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
