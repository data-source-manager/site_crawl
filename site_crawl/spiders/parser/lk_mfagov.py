# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class LK_mfagovParser(BaseParser):
    name = 'lk_mfagov'
    
    # 站点id
    site_id = "bd0f4927-466f-439f-aa22-ee4ff7daf270"
    # 站点名
    site_name = "斯里兰卡外交部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "bd0f4927-466f-439f-aa22-ee4ff7daf270", "source_name": "斯里兰卡外交部", "direction": "lk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("23cc4ec8-b7fe-37f7-b567-967ae974d836", "媒体发布", "", "政治"),
            ("91236780-2f72-11ed-a768-d4619d029786", "媒体发布/事工新闻", "https://mfa.gov.lk/category/news/media-releases/", "政治"),
            ("9123680c-2f72-11ed-a768-d4619d029786", "媒体发布/使命新闻", "https://mfa.gov.lk/category/mission-news/", "政治"),
            ("1cab1b54-e976-4ac5-acf0-218de8b88dc8", "媒体发布/媒体声明", "https://mfa.gov.lk/category/media-briefings/", "政治"),
            ("ad61beef-e39b-4fc0-899d-ee762f573ba6", "媒体发布/新闻简报", "https://mfa.gov.lk/category/media-briefings/", "政治"),
            ("d9fd049a-22f1-4c4d-b3fc-d347b85c994d", "媒体发布/来自其他来源的新闻", "https://mfa.gov.lk/category/news-from-other-media-news-from-other-media/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//h2[@class='entry-title']/a/@href").extract() or []
        pub_times = response.xpath("//span[@class='posted-on']//text()").extract() or []
        if news_urls:
            for index, news_url in enumerate(news_urls):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                self.Dict[news_url] = pub_times[index]
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h2[@class='entry-title']/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        23.03.2021
        """
        datePublished_str = self.Dict[response.url]
        if datePublished_str:
            dt = datetime.strptime(datePublished_str.strip(), "%d.%m.%Y")
            return datetime_helper.parseTimeWithOutTimeZone(dt, site_name="斯里兰卡外交部")

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='entry-content']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "p", "span"] or news_tag.root.get("class",
                                                                                                         "") == 'field field--intro':
                    if news_tag.xpath("./img"):
                        con_img = self.parse_img(response, news_tag, img_xpath="./img/@src")
                        if con_img:
                            content.append(con_img)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        """"
            可以对一个标签下存在多个段落进行解析
        """
        dic = {}
        cons = news_tag.xpath(".//text()").extract() or ""
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

    def parse_img(self, response, news_tag, img_xpath='', img_des=''):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath(img_xpath).extract_first()

        if img and ".html" not in img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": None,
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
        videoUrl = news_tag.xpath(".//iframe/@src").extract_first()
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
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
