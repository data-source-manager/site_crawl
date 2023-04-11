# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

import requests
from lxml import etree

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class RU_riaParser(BaseParser):
    name = 'ru_ria'
    
    # 站点id
    site_id = "e30063e0-f62f-4428-9394-f55355372012"
    # 站点名
    site_name = "俄罗斯新闻社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e30063e0-f62f-4428-9394-f55355372012", "source_name": "俄罗斯新闻社", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91235024-2f72-11ed-a768-d4619d029786", "军队", "https://ria.ru/defense_safety/", "政治"),
            ("91234ff2-2f72-11ed-a768-d4619d029786", "政治", "https://ria.ru/politics/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="list-item"]')
        if news_urls:
            for news_url in list(set(news_urls)):
                url = news_url.xpath(".//a[@class='list-item__image']/@href").extract_first()
                if not url.startswith('http'):
                    url = urljoin(response.url, url)

                read_count = news_url.xpath(".//div[@class='list-item__views-text']/text()").extract_first()
                if read_count:
                    self.Dict[url] = read_count
                else:
                    self.Dict[url] = 0

                yield url

    def get_title(self, response) -> str:
        title = response.xpath("//meta[@property='og:title']/@content").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = response.xpath("//meta[@property='article:published_time']/@content").extract_first()
        if datePublished_str:
            dt_ = datetime_helper.fuzzy_parse_timestamp(datePublished_str)
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt_))
            return str(dt)
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags_node = response.xpath(
            "//div[@class='article m-article m-ria']//a[@class='article__tags-item']/text()").getall()
        if tags_node:
            tags_list.extend(tags_node)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath("//div[@class='article__announce']//img")
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath("//div[@class='article__text']")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
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

    def parse_text(self, news_tag) -> list:
        """
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip() and ".css-" not in x:
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@src').extract_first()

        if img and ".html" not in img and 'data:image/svg+xml,' not in img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath('./@alt').extract_first(),
                   "src": img}
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
        url = response.url
        id = re.findall("(\d+).html", url)[0]
        headers = {
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        }
        api_url = 'https://ria.ru/services/article/add_emoji/?article_id={}&emotion=s1'.format(id)
        jspm_data = requests.get(api_url, headers=headers).json()
        like_count_str = jspm_data['s1']

        if like_count_str:
            like_count = int(like_count_str)

        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        headers = {
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        }
        url = response.url
        date_time, id = re.findall("/(\d+)/.*?(\d+).html", url)[0]
        api_url = 'https://ria.ru/services/dynamics/{}/{}.html'.format(date_time, id)
        html_node = requests.get(api_url, headers=headers).text
        ress = etree.HTML(html_node)
        read_count_str = ress.xpath("//span[@class='statistic__item m-views']/text()")
        if read_count_str:
            read_count = int(read_count_str[0])
        return read_count
        return self.Dict.get(response.url)

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
