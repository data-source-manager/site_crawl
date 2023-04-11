# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class WilsoncenterParser(BaseParser):
    name = 'wilsoncenter'
    
    # 站点id
    site_id = "387f07dc-51a3-4f78-b5e7-d34da86d2853"
    # 站点名
    site_name = "伍德罗威尔逊国际学者中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "387f07dc-51a3-4f78-b5e7-d34da86d2853", "source_name": "伍德罗威尔逊国际学者中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("0a33e391-149d-4c90-bb25-8931991784df", "研究与分析", "https://www.wilsoncenter.org/insight-analysis?_page=1&keywords=&_limit=10&topics=636,2,126,131,421,132,130,978,152,151,153,164,185,326,675,336,187,186,188,189,190,191,192,193,170,181,182,184,183,180,680,496,566,301,506,1001,501,324,561,1002,167", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="faceted-search-results"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//span[@class="insight-detail-hero-author-byline-link-text"]/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[contains(@class,"datetime-date")]/text()|'
                               '//div[@class="event-hero-date"]/text()|'
                               '//span[@class="insight-detail-hero-author-byline-text -date"]/text()|'
                               '//meta[@property="article:modified_time"]/@content|'
                               '//meta[@name="shareaholic:article_published_time"]/@content').extract_first()

        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[contains(@class,"tags-items")]/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        video_list = response.xpath('//div[@class="video-container"]/iframe|//div[@class="css-15x5cbk"]/iframe')
        if video_list:
            con_img = self.parse_media(response, video_list)
            if con_img:
                content.append(con_img)
        img = response.xpath('//div[contains(@class,"hero-image-inner")]//img|'
                             '//div[@class="desktopArticle"]//img|//header[@class="entry-header"]//img')
        if img:
            complete_url = urljoin(response.url, img.xpath("./@src").extract_first())
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(complete_url) + '.jpg',
                   "description": "".join(img.xpath('.//img/@alt').extract()).strip(),
                   "src": complete_url
                   }
        news_tags = response.xpath('//div[contains(@class,"wysiwyg-content")]//p|'
                                   '//span[contains(@class,"wysiwyg-content")]//p|'
                                   '//div[@class="desktopArticle"]/*|//bdi[@class="css-jm5bon"]/*')
        img_list = response.xpath('//div[contains(@class,"hero-image-inner")]//img|//div[@class="desktopArticle"]//img|'
                                  '//header[@class="entry-header"]//img|//div[@class="separator"]//img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)
        news_tags = response.xpath('//div[contains(@class,"wysiwyg-content")]//p|'
                                   '//span[contains(@class,"wysiwyg-content")]//p|'
                                   '//div[@class="desktopArticle"]/*|//div[@class="news-text single"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "a"]:
                    text_dict = self.parseOnetext(news_tag)
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

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("./@src").extract_first()
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
