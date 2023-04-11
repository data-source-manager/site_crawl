# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class NduParser(BaseParser):
    name = 'ndu'
    
    # 站点id
    site_id = "2f69335c-821d-4a6c-8ca1-dbf8065f993a"
    # 站点名
    site_name = "陆军军事学院战略领导与发展中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "2f69335c-821d-4a6c-8ca1-dbf8065f993a", "source_name": "陆军军事学院战略领导与发展中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("2c3db73e-185e-442e-9f18-e9c8d8c4cd27", "出版社", "https://ndupress.ndu.edu/", "政治"),
            ("1fa39eef-34bf-e041-678e-57b4ae13ec88", "研究中心", "", "政治"),
            ("5751ca9d-7d81-4088-9f8e-6650f32e5c43", "研究中心/战略", "https://inss.ndu.edu/Portals/82/Documents/Five-Year-Research-Strategy%20-2017-2021.pdf?ver=2016-11-10-102126-063", "政治"),
            ("9a1f9bf6-53d3-4017-9609-83de31e4f62e", "研究中心/武器", "https://wmdcenter.ndu.edu/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.pdfUrl = ""

    def parse_list(self, response) -> list:
        if "Documents" in response.url:
            self.pdfUrl = response.url
            yield response.url
        if "ndupress" in response.url:
            news_urls = response.xpath(
                '//a[@class="storyInner"]/@href|//div[contains(@class,"pub-block")]/a/@href').extract() or []
            if news_urls:
                for news in list(set(news_urls)):
                    url = urljoin(response.url, news)
                    yield url
        if "wmdcenter" in response.url:
            news_urls = response.xpath('//a[@class="da_news_link"]/@href').extract() or []
            if news_urls:
                for news in list(set(news_urls)):
                    url = urljoin(response.url, news)
                    yield url

    def get_title(self, response) -> str:
        if "Documents" in response.url:
            return ""
        title = response.xpath('//meta[@name="twitter:title"]/@content').extract_first(default="")
        if not title:
            title = response.xpath('//h1[@class="title"]/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        if "Documents" in response.url:
            return []
        author_list = []
        author = response.xpath('//p[@class="info"]/span[1]/text()').extract()
        if author:
            if "and" in author:
                author = author.split("and")
                for x in author:
                    if x.strip():
                        author_list.extend(x.strip())
            else:
                author_list.append(author[0].replace("By", "").strip())
        return author_list

    def get_pub_time(self, response) -> str:
        if "Documents" in response.url:
            return ""
        # Feb. 12, 2021
        pub = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if pub:
            if "." in pub:
                pub = str(datetime.strptime(pub, "%b. %d, %Y"))
            else:
                pub = str(datetime.strptime(pub, "%B %d, %Y"))
        else:
            pub = "9999-01-01 00:00:00"
        return pub

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        if "Documents" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
        else:
            if "wmdcenter" in response.url:
                news_tags = response.xpath('//div[@class="image-wrapper"]/img|'
                                           '//div[@class="body"]/p'
                                           )
                if news_tags:
                    for news_tag in news_tags:
                        if news_tag.root.tag == "img":
                            img_dict = self.parse_img(response, news_tag)
                            content.append(img_dict)
                        if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p", "li"]:
                            text_dict = self.parse_text(news_tag)
                            if text_dict:
                                content.append(text_dict)
                return content
            if "ndupress" in response.url:
                news_tags = response.xpath('//div[@class="image-wrapper"]/img|'
                                           '//div[@class="body"]/p|'
                                           '//div[@class="body"]/p/a[contains(@href,"pdf")]'
                                           )
                if news_tags:
                    for news_tag in news_tags:
                        if news_tag.root.tag == "img":
                            img_dict = self.parse_img(response, news_tag)
                            content.append(img_dict)
                        if news_tag.root.tag == "a":
                            file_dict = self.parse_file(response, news_tag)
                            content.append(file_dict)
                        if news_tag.root.tag in ["h2", "h3", "h5", "strong", "p", "li"]:
                            text_dict = self.parse_text(news_tag)
                            if text_dict.get("data"):
                                content.append(text_dict)
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
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("./@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
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
