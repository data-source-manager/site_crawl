# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin, unquote

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class ArmywarcollegeParser(BaseParser):
    name = 'armywarcollege'
    
    # 站点id
    site_id = "2adff366-9ce1-4c1b-b999-985b1b59a5aa"
    # 站点名
    site_name = "美国陆军战争学院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "2adff366-9ce1-4c1b-b999-985b1b59a5aa", "source_name": "美国陆军战争学院", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9123239c-2f72-11ed-a768-d4619d029786", "新闻档案", "https://www.armywarcollege.edu/News/archives.cfm", "军事"),
            ("9123236a-2f72-11ed-a768-d4619d029786", "消息", "https://www.armywarcollege.edu/News/index.cfm", "军事"),
            ("91232338-2f72-11ed-a768-d4619d029786", "视频", "https://www.armywarcollege.edu/videos/index.cfm", "军事"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.detail = {}

    def parse_list(self, response) -> list:
        if response.url.startswith('https://www.armywarcollege.edu/videos'):
            for item in response.xpath('//section'):
                title = item.xpath('.//h4/text()').extract_first(default="")
                desc = item.xpath('.//p/text()').extract_first(default="")
                video_url = item.xpath('.//div/object/@data').extract_first(default="")
                fake_url = f'http://httpbin.org/base64/video{title}.pdf'
                self.detail[fake_url] = {
                    'title': title,
                    'desc': desc,
                    'origin_url': video_url,
                    'real_url': fake_url
                }
                yield {'origin_url': video_url, 'real_url': fake_url}
        elif response.url.startswith('https://www.armywarcollege.edu/News/index.cfm'):
            news_urls = response.xpath(
                '//section//a/@href').extract() or []
            if news_urls:
                for news_url in list(set(news_urls)):
                    news_url = urljoin(response.url, news_url)
                    yield news_url
        elif response.url.startswith('https://www.armywarcollege.edu/News/archives.cfm'):
            news_items = response.xpath('//tr[td/a]')
            for item in news_items:
                url = item.xpath('.//a/@href').extract_first(default="")
                if not url:
                    continue
                real_url = urljoin(response.url, url)
                title = item.xpath('.//a/text()').extract_first(default="")
                fake_url = f'http://httpbin.org/base64/article{title}.pdf'
                pub_time = item.xpath('./td[2]/text()').extract_first(default="")
                pub_time = str(datetime_helper.fuzzy_parse_datetime(pub_time))
                self.detail[fake_url] = {
                    'origin_url': real_url,
                    'title': title,
                    'real_url': fake_url,
                    'pub_time': pub_time
                }
                yield {
                    'origin_url': real_url,
                    'real_url': fake_url,
                }

    def get_title(self, response) -> str:
        url = unquote(response.url, 'utf-8')
        if 'httpbin.org/base64' in url:
            return self.detail[url].get("title")
        else:
            title = response.xpath('//meta[@propety="og:title"]/@content').extract_first(default="")
            return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        url = unquote(response.url, 'utf-8')
        if 'httpbin.org/base64' in url:
            if "video" in url:
                return "9999-01-01 00:00:00"
            return self.detail[url].get("pub_time")
        else:
            pub_time = response.xpath('//section/h1/following-sibling::p[1]/span/text()').extract_first(default="")
            if pub_time:
                pub_time = datetime_helper.fuzzy_parse_timestamp(pub_time.strip())
                pub_time = str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
                return pub_time
            else:
                return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        url = unquote(response.url, 'utf-8')

        content = []
        if 'httpbin.org/base64' in url:
            return [{
                "type": "video",
                "src": self.detail[url].get("real_url"),
                "name": None,
                "description": self.detail[url].get("desc"),
                "md5src": self.get_md5_value(self.detail[url].get("real_url")) + ".mp4"
            }]
        if 'httpbin.org/base64' in url and url.endswith('.pdf'):
            return [{
                "type": "file",
                "src": self.detail[url].get("real_url"),
                "name": self.detail[url].get("title"),
                "description": None,
                "md5src": self.get_md5_value(self.detail[url].get("real_url")) + ".pdf"
            }]
        elif url.startswith('https://www.armywarcollege.edu/News/article/'):
            # 消息
            news_tags = response.xpath(
                '//a[img and @data-fancybox="group"]|'
                '//section/p')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag == 'p':
                        text_dict = self.parse_text(news_tag)
                        if text_dict.get("data"):
                            content.append(text_dict)
                    if news_tag.root.tag == 'a':
                        img_dict = self.parse_img(response, news_tag)
                        if img_dict:
                            content.append(img_dict)
            return content

    def get_detected_lang(self, response) -> str:
        return "en"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('href'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('data-caption'),
               "src": img_url
               }
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath(".//a/text()").extract_first(),
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url, news_tag.xpath("").extract_first())
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
