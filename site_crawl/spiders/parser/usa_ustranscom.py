# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class UsaUstranscomParser(BaseParser):
    name = 'ustranscom'
    
    # 站点id
    site_id = "2ac80ff4-f614-4b41-a373-cc05888ab8b4"
    # 站点名
    site_name = "运输司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "2ac80ff4-f614-4b41-a373-cc05888ab8b4", "source_name": "运输司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91236ffa-2f72-11ed-a768-d4619d029786", "新闻室", "https://www.ustranscom.mil/cmd/panews.cfm", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h2[@class="entry-title"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@id="headliner"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[@class="published-date"]/text()').extract()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(''.join(time_).strip())
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="photo-container"]/img|'
                                  '//div[@data-u="slides"]/div')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))

        news_tags = response.xpath('//div[@class="byline-release-pubdate"]/following-sibling::*[1]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    if news_tag.xpath('./img').extract_first():
                        for x in news_tag.xpath('./img'):
                            con_img = self.parse_img(response, x)
                            if con_img:
                                content.append(con_img)
                    text_dict = self.parseOneText(news_tag)
                    if text_dict:
                        content.extend(text_dict)

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

    def parseOneText(self, news_tag) -> list:
        """"
            一个标签下只有一段但是存在其他标签
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            if "".join(cons).strip():
                dic['data'] = "".join(cons).strip()
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        if news_tag.root.tag == "div":
            img = news_tag.xpath(".//img/@src").extract_first()
            if img:
                img_url = urljoin(response.url, img)
                dic = {"type": "image",
                       "name": news_tag.attrib.get('title', None),
                       "md5src": self.get_md5_value(img_url) + '.jpg',
                       "description": "".join(news_tag.xpath('.//div[@class="caption-bg"]//text()').extract()),
                       "src": img_url}
                return dic
        else:
            img = news_tag.xpath('./@src').extract_first()
            if img.startswith("data:image"):
                return {}
            if img:
                img_url = urljoin(response.url, img)
                dic = {"type": "image",
                       "name": news_tag.attrib.get('title', None),
                       "md5src": self.get_md5_value(img_url) + '.jpg',
                       "description": news_tag.xpath('./@alt').extract_first(),
                       "src": img_url}
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

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("").extract_first()
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
