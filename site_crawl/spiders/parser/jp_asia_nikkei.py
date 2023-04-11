# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class JpasiaParser(BaseParser):
    name = 'asia'
    channel = [
        {
            'url': 'https://asia.nikkei.com/Location/East-Asia/China',
            'direction': 'jp',
            'source_name': '日经亚洲',
            'site_board_name': '地点新闻/中国',
            'board_theme': '政治',
            'if_front_position': False
        }, {
            'url': 'https://asia.nikkei.com/Location/East-Asia/Taiwan',
            'direction': 'jp',
            'source_name': '日经亚洲',
            'site_board_name': '地点新闻/台湾',
            'board_theme': '政治',
            'if_front_position': False
        }, {
            'url': 'https://asia.nikkei.com/Politics',
            'direction': 'jp',
            'source_name': '日经亚洲',
            'site_board_name': '政治',
            'board_theme': '政治',
            'if_front_position': False
        }, {
            'url': 'https://asia.nikkei.com/Editor-s-Picks/China-up-close',
            'direction': 'jp',
            'source_name': '日经亚洲',
            'site_board_name': '中国近距离',
            'board_theme': '政治',
            'if_front_position': False
        }, {
            'url': 'https://asia.nikkei.com/Opinion',
            'direction': 'jp',
            'source_name': '日经亚洲',
            'site_board_name': '观点国',
            'board_theme': '政治',
            'if_front_position': False
        }, {
            'url': 'https://asia.nikkei.com/Politics/International-relations',
            'direction': 'jp',
            'source_name': '日经亚洲',
            'site_board_name': '国际关系',
            'board_theme': '政治',
            'if_front_position': False
        },
        {
            'url': 'https://asia.nikkei.com/Location/East-Asia/Mongolia',
            'direction': 'jp',
            'source_name': '日经亚洲',
            'site_board_name': '蒙古',
            'board_theme': '政治',
            'if_front_position': False
        },

    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h4[@class="card-article__headline"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[contains(@class,"article-header__date")]/@datetime|'
                               '//span[contains(@class," article__date")]/@datetime').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="article__content"]/div/img')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))

        news_tags = response.xpath('//div[@class="ezrichtext-field"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parse_text(news_tag)
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
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": response.xpath('.//span[@class="article__caption"]/text()').extract_first(),
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
