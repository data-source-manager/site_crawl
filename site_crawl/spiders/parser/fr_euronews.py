# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class FR_euronewsParser(BaseParser):
    name = 'fr_euronews'
    
    # 站点id
    site_id = "910b0c58-2038-4ea0-a850-7ab38c04b4c1"
    # 站点名
    site_name = "Euronews"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "910b0c58-2038-4ea0-a850-7ab38c04b4c1", "source_name": "Euronews", "direction": "fr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("912362da-2f72-11ed-a768-d4619d029786", "世界", "https://www.euronews.com/programs/world", "政治"),
            ("9123632a-2f72-11ed-a768-d4619d029786", "辩论与意见", "https://www.euronews.com/my-europe/debates-and-opinion", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//h3[contains(@id,'-listing_library')]/a/@href|//h3[contains(@id,'-more_news_themes')]/a/@href|//h1[contains(@id,'program_topstories_newsy')]/a/@href").extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//meta[@property='og:title']/@content").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        author_a = response.xpath(
            "//header[@class='o-article__header']/div[@class='c-article-contributors']//b/text()").get()
        if author_a:
            author_list.append(author_a.strip())
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = response.xpath("//meta[@name='date.updated']/@content").get()
        if datePublished_str:
            dt = datetime_helper.fuzzy_parse_timestamp(datePublished_str)
            Date_mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt))
            return str(Date_mt)
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags_node = response.xpath("//meta[@name='keywords']/@content").get()
        if tags_node:
            for tag in tags_node.split(","):
                tags_list.append(tag)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[contains(@class,'c-article-content')]/*|"
                                   "//div[contains(@class,'c-article-content')]//figure|"
                                   "//div[@class='c-video-player__container']/img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "p"]:
                    if news_tag.xpath("./img"):
                        con_img = self.parse_img(response, news_tag, img_xpath="./@src")
                        if con_img:
                            content.append(con_img)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src", img_des="./@alt")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag == "figure":
                    con_img = self.parse_img(response, news_tag, img_xpath=".//img/@src",
                                             img_des=".//figcaption//span[@class='widget__captionText']/text()")
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
                   "description": news_tag.xpath(img_des).extract_first() or None,
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
