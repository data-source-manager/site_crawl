# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

import langdetect

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class UsfkParser(BaseParser):
    name = 'usfk'
    
    # 站点id
    site_id = "07f07980-7b4e-4f6a-98ac-b3946edbfd7d"
    # 站点名
    site_name = "驻韩美军"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "07f07980-7b4e-4f6a-98ac-b3946edbfd7d", "source_name": "驻韩美军", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("bb4624bb-aa92-a823-bd51-dacec6dbbbb4", "媒体", "", "政治"),
            ("f061d6dd-8dee-4952-b1bd-e45d92fa9834", "媒体/新闻室", "https://www.usfk.mil/Media/Newsroom/", "政治"),
            ("28b4fd93-8ab1-4b5e-8ead-8cc5ab8d64c3", "媒体/新闻稿", "https://www.usfk.mil/Media/Press-Products/", "政治"),
            ("52b43579-448f-4c0d-a287-79d0d2e5b42b", "媒体/演讲", "https://www.usfk.mil/Media/Press-Products/Speeches-Transcripts/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        urls = response.xpath('//a[@class="ex-link"]/@href|//p[@class="title"]/a/@href').extract()
        if urls:
            for url in urls:
                if "2682073" in url or "usfk-covid-19-archived-updates" in url:
                    continue
                yield urljoin(response.url, url)
        # yield "https://www.usfk.mil/Media/Press-Products/Speeches-Transcripts/Article/1688603/adm-davison-remarks-unccfcusfk-change-of-command-ceremony/"

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="twitter:title"]/@content').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        # March 10, 2022
        pub = response.xpath(
            '//meta[@itemprop="datePublished"]/@content').extract_first()
        if pub:
            try:
                pub_time = str(datetime.strptime(pub, "%B %d, %Y"))
            except:
                pub_time = str(datetime.strptime(pub.split(".")[0].replace("T", " "), "%Y-%m-%d %H:%M:%S"))
            return pub_time
        else:
            pub = response.xpath(
                '//div[@class="category-date"]/text()').extract()
            if pub:
                pub = "".join(pub).replace("|", "").strip()
                pub_time = str(datetime_helper.fuzzy_parse_datetime(pub))
            else:
                pub_time = "9999-01-01 00:00:00"
            return pub_time

    def get_tags(self, response) -> list:
        tag_list = []
        tags = response.xpath('//div[@class="tags"]//a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tag_list.append(tag.strip())
        return tag_list

    def get_content_media(self, response) -> list:
        content = []

        imgs = response.xpath('//div[@class="item"]')
        if imgs:
            for img in imgs:
                img_dic = self.parse_img(response, img)
                if img_dic:
                    content.append(img_dic)

        img_list_length = len(imgs)

        news_tags = response.xpath(
            '//div[@class="body"]//p|//div[@class="body"]//p/img|'
            '//div[@class="body"]/span|'
            '//div[@class="body"]/h3|'
            '//div[@class="body"]/h5|'
            '//div[@class="body"]/div[contains(@class,"media-inline")]|'
            '//div[@class="body"]/div/div[@class="header"]/span|//div[@class="body"]/text()')
        if news_tags:
            for news_tag in news_tags:
                if type(news_tag.root) == str:
                    dic = {}
                    if news_tag.root.strip():
                        dic["data"] = news_tag.root.strip()
                        dic["type"] = "text"
                        content.append(dic)
                else:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "strong", "div"]:
                        if news_tag.root.tag == "div":
                            img_url = urljoin(response.url,
                                              news_tag.xpath(".//img/@src").extract_first())
                            dic = {"type": "image",
                                   "name": None,
                                   "md5src": self.get_md5_value(img_url) + '.jpg',
                                   "description": news_tag.xpath(".//img/@alt").extract_first(),
                                   "src": img_url
                                   }
                            content.append(dic)
                        if news_tag.root.tag == "img":
                            img_url = urljoin(response.url,
                                              news_tag.xpath("./@src").extract_first())
                            dic = {"type": "image",
                                   "name": None,
                                   "md5src": self.get_md5_value(img_url) + '.jpg',
                                   "description": news_tag.xpath("./@alt").extract_first(),
                                   "src": img_url
                                   }
                            content.append(dic)
                        text_list = self.parse_text(news_tag)
                        if text_list:
                            content.extend(text_list)

        news_content = []
        for i, con in enumerate(content):
            if i == img_list_length:
                continue
            if i == img_list_length + 1:
                con["data"] = content[i - 1].get("data") + con.get("data")
            news_content.append(con)
        return news_content

    def get_detected_lang(self, response) -> str:
        title = self.get_title(response)
        if title:
            return langdetect.detect(f"{title}")
        else:
            print('error, no title url:' + response.url)
            return ''

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        img = news_tag.xpath(".//img/@src").extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath("./p/text()").extract_first(),
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
