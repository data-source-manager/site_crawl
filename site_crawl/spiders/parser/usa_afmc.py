# -*- coding: utf-8 -*-
"""
@fix: liyun-2023-01-07: 图像数据解析异常修正
"""

import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class UsaAfmcParser(BaseParser):
    name = 'afmc'
    
    # 站点id
    site_id = "cc798196-936e-f9f2-a844-7a1e7521ba1d"
    # 站点名
    site_name = "美国空军装备司令部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "cc798196-936e-f9f2-a844-7a1e7521ba1d", "source_name": "美国空军装备司令部", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8c4316-fe6f-11ec-a30b-d4619d029786", "照片", "https://www.afmc.af.mil/News/Photos/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.title = {}

    def parse_list(self, response) -> list:
        if "Photos" in response.url:
            news_urls = response.xpath('//figure[@class="gallery_container"]')
            if news_urls:
                for news_url in news_urls:
                    url = news_url.xpath('./a/@href').extract_first()
                    title = news_url.xpath('.//h1[@class="gallery_title"]//text()').extract_first()
                    self.title[url.replace("http", "https")] = title
                    yield url
        else:
            news_urls = response.xpath('//h1/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "Photos" in response.url:
            return self.title[response.url]
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        if "Photos" in response.url:
            return []
        author_list = []

        authors = response.xpath('//div[@class="meta"]/ul/li[2]/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.replace("By", "").strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "Photos" in response.url:
            return "9999-01-01 00:00:00"
        time_ = response.xpath('//time/@datetime').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        if "Photos" in response.url:
            return []
        tags = response.xpath('//a[@class="article-detail-tag"]/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    """
    @fix: liyun-2023-01-07: 图像数据解析异常修正
    """

    def get_content_media(self, response) -> list:

        content = []
        main_tag_xpath = '//div[@id="dnn_ctr1736_ModuleContent"]'
        # 解析图片
        image_urls = response.xpath(f'{main_tag_xpath}//a/@href').extract()
        # 过滤
        for url in list(set(image_urls)):
            suffix = url.split(".")[-1].upper()
            if suffix not in ["JPG", "PNG"]:
                continue
            img_url = urljoin(response.url, url)
            content.append({
                "type": "image",
                "name": None,
                "md5src": self.get_md5_value(img_url) + f'.{suffix}',
                "description": "",
                "src": img_url
            })
        # 解析正文
        for tag in response.xpath(f'{main_tag_xpath}//div[@class="details-content"]/*') or []:
            if tag.root.tag in ["p"]:
                texts = self.parseOnetext(tag)
                texts and content.extend(texts)
        # 解析照片详细数据
        for tag in response.xpath(f'{main_tag_xpath}//div[@class="details-image-details tabular-details"]/div') or []:
            text = " ".join(tag.xpath(".//span/text()").extract()).strip()
            text and content.append({"data": text, "type": "text"})

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
            oneCons = "".join(cons).strip()
            if "learn more information" in oneCons:
                return []
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
        videoUrl = news_tag.xpath("").extract_first()
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
