# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UkbbcenParser(BaseParser):
    name = 'uk_bbcen'
    
    # 站点id
    site_id = "a13b2c0d-fc07-4cfe-a44f-b96870ef620b"
    # 站点名
    site_name = "BBC英文网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "a13b2c0d-fc07-4cfe-a44f-b96870ef620b", "source_name": "BBC英文网", "direction": "uk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b32b4-fe6f-11ec-a30b-d4619d029786", "世界", "https://www.bbc.com/news/world", "政治"),
            ("4a8b3264-fe6f-11ec-a30b-d4619d029786", "乌克兰战争", "https://www.bbc.com/news/world-60525350", "政治"),
            ("4a8b3336-fe6f-11ec-a30b-d4619d029786", "亚洲", "https://www.bbc.com/news/world/asia", "政治"),
            ("4a8b32fa-fe6f-11ec-a30b-d4619d029786", "科技", "https://www.bbc.com/news/technology", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "asia" in response.url:
            news_urls = response.xpath('//article//h3/a/@href').extract() or ""
        else:
            news_urls = response.xpath(
                "//div[@class='gel-layout gel-layout--equal']//div[contains(@class,'gs-c-promo-body--')]/div/a[contains(@class,'gs-c-promo-heading')]/@href|"
                "//h3[contains(@class,'lx-stream-post__header-title')]/a/@href").extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@id='main-heading']/text()|"
                               "//h1[@class='gel-trafalgar-bold qa-story-headline gs-u-mv+']/text()|"
                               "//h1[@id='main-heading']/span/text()|"
                               "//h1[@id='lx-event-title']/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        author_str = response.xpath("//p[contains(@class,'-Contributor')]/span/strong/text()").get()
        if author_str:
            author_list.append(author_str.replace("By", ""))
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//time/@datetime').get()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath(
            "//h2[text()[contains(.,'Related Topics')]]/preceding::div/following::div[contains(@class,'-Cluster')]/ul/li/a[contains(@class,'StyledLink')]/text()").getall()
        if tags:
            tags = list(set(tags))
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath("//div[contains(@class,'-RichTextContainer')]/*|"
                                   "//div[@data-component='image-block']//figure//img|"
                                   "//li/article//div[@class='lx-stream-post-body']/*|"
                                   "//li/article//div[@class='lx-stream-post-body']//img")
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
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
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
            oneCons = "".join(cons).strip()
            if oneCons:
                dic['data'] = oneCons
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
        img = news_tag.xpath('./@src').extract_first()
        if img.startswith("data:image/gif;base64"):
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
        if self.Dict.get(response.url):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        repost_source_str = response.xpath("//p[contains(@class,'ssrcss-ugte5s-Contributor')]/span/strong/text()").get()
        if repost_source_str:
            repost_source = repost_source_str
            self.Dict[response.url] = repost_source_str
        return repost_source
