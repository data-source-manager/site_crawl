# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaJcsParser(BaseParser):
    name = 'jcs'
    
    # 站点id
    site_id = "bb25d524-8b4b-449a-a9f2-4ddca3106729"
    # 站点名
    site_name = "美国参联会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "bb25d524-8b4b-449a-a9f2-4ddca3106729", "source_name": "美国参联会", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8bf974-fe6f-11ec-a30b-d4619d029786", "新闻", "https://www.jcs.mil/Media/News/", "政治"),
            ("4a8bf9e3-fe6f-11ec-a30b-d4619d029786", "理事会", "", "政治"),
            ("4a8bf9e4-fe6f-11ec-a30b-d4619d029786", "理事会/战略、计划和政策", "https://www.jcs.mil/Directorates/J5-Strategy-Plans-and-Policy/", "军事"),
            ("4a8bf9e2-fe6f-11ec-a30b-d4619d029786", "相片", "https://www.jcs.mil/Media/Photos/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id='bb25d524-8b4b-449a-a9f2-4ddca3106729'
    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//span[@class="title"]/a/@href|'
            '//div[@class="ImageGallerylvImage"]/a/@href'
        ).extract() or []
        # 板块(理事会/战略、计划和政策) 特殊处理
        if response.url == 'https://www.jcs.mil/Directorates/J5-Strategy-Plans-and-Policy/':
            yield response.url
        for news_url in news_urls:
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "Photos" in response.url:
            return "美国参联会_photos"
        title = response.xpath('//h1[@itemprop="headline"]/text()').extract_first(default="")
        # 战略、板块(理事会/计划和政策) 特殊处理
        if not title:
            title = "".join(response.xpath('//div[@class="container-title"]/span/text()').extract() or [])
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@class="tags"]/div/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@itemprop="articleBody"]/*'
            '|//div[@class="ImageImg"]//img'
            '|//span[@id="spanCaption"]'
            # 板块(理事会/战略、计划和政策)
            '|//table[@class="customjcstext"]//p'
            '|//div[@class="jcs_bio_frame"]/img'
        )
        for news_tag in news_tags:
            if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                text_dict = self.parse_text(news_tag)
                if text_dict:
                    content.extend(text_dict)
            if news_tag.root.tag == "ul":
                for con in news_tag.xpath('./li'):
                    con_text = self.parseOnetext(con)
                    if con_text:
                        content.append(con_text)
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
        img = news_tag.xpath('.//@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//@alt').extract()).strip(),
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
