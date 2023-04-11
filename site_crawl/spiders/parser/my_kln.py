# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class MyklnParser(BaseParser):
    name = 'kln'
    
    # 站点id
    site_id = "6f4d3b0c-f894-4a73-b5e1-976e52d9cd45"
    # 站点名
    site_name = "马来西亚外交部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "6f4d3b0c-f894-4a73-b5e1-976e52d9cd45", "source_name": "马来西亚外交部", "direction": "my", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f1fb3a7a-57c1-3280-8713-0f0e8848ebb8", "公共外交", "", "政治"),
            ("912358b2-2f72-11ed-a768-d4619d029786", "公共外交/新闻稿", "https://www.kln.gov.my/web/guest/mfa-news", "政治"),
            ("9123593e-2f72-11ed-a768-d4619d029786", "公共外交/演讲与声明", "https://www.kln.gov.my/web/guest/speeches-statements", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.urlPubdict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@id="Press Releases"]//tbody[@class="table-data"]/tr|'
                                   '//tbody[@class="table-data"]/tr')
        if news_urls:
            for news_url in news_urls:
                url = news_url.xpath(".//a/@href").extract_first()
                # if "nheritRedirect=true" not in url and "press-releases" in response.url:
                pub = news_url.xpath("./td[last()]/text()").extract_first()
                self.urlPubdict[url] = pub
                yield urljoin(response.url, url)

    def get_title(self, response) -> str:
        title = response.xpath('//h3[@class="header-title"]/span/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        pub = self.urlPubdict[response.url]
        if pub:
            pub_time = datetime_helper.fuzzy_parse_timestamp(pub)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="journal-content-article"]/*|'
                                   '//div[@class="journal-content-article"]/div/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "a", "li"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)

        return content

    def get_detected_lang(self, response) -> str:
        return "en"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath("").extract() or ""
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
        img = news_tag.xpath('./@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.attrib.get('alt'),
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
