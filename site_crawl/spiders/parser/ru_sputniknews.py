# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import requests
from parsel import Selector

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class RusputniknewsParser(BaseParser):
    name = 'ru_sputniknews'
    
    # 站点id
    site_id = "06777efc-4591-4c9d-8a7d-570ef32b03a1"
    # 站点名
    site_name = "俄罗斯卫星通讯社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "06777efc-4591-4c9d-8a7d-570ef32b03a1", "source_name": "俄罗斯卫星通讯社", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e7010244-7607-11ed-ad4d-d4619d029786", "俄中关系", "https://sputniknews.cn/russia_china_relations/", "政治"),
            ("e700a84e-7607-11ed-ad4d-d4619d029786", "国际", "https://sputniknews.cn/category_guoji/", "政治"),
            ("95b54c14-62cb-4f7d-aa54-d87594e71df3", "播客", "https://sputniknews.cn/podcast/", "政治"),
            ("e700ef70-7607-11ed-ad4d-d4619d029786", "评论", "https://sputniknews.cn/opinion/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@class='list__content']/a[@class='list__title']/@href").extract()
        if "podcast" in response.url:
            news_urls = response.xpath('//a[@class="cell-audio__link"]/@href').extract()

        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = response.xpath('//meta[@property="article:author"]/@content').extract_first(default="")
        if author_list:
            return [author_list]

        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath("//meta[@property='article:published_time']/@content").get()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//a[@class='tag__text']/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[@class='article__block']/div|"
            "//div[@class='article__block']//img|"
            "//div[@class='article__announce-text']|"
            "//div[@class='article__announce']//img|"
            "//meta[@property='og:audio']")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p",
                                         "div"] and "article__text" in news_tag.root.get(
                    "class", "") or "article__announce-text" in news_tag.root.get("class", ""):
                    text_dict = self.parseOneText(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "meta":
                    audio_dict = self.parse_media(response, news_tag, media_type="mp3")
                    if audio_dict:
                        content.append(audio_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    for li in news_tag.xpath("./li"):
                        text_dict = self.parse_text(li)
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
                if "欢迎收听今天的" in x:
                    continue
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
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
            if "欢迎收听今天的节目" in "".join(cons):
                return []
            if "".join(cons).strip():
                dic['data'] = "".join(cons).strip()
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag, img_xpath='', img_des=''):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath(img_xpath).extract_first()
        if "data:image" in img:
            return {}
        if img:
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

    def parse_media(self, response, news_tag, media_type):
        videoUrl = news_tag.xpath("./@content").extract_first()

        suffix = f".{media_type}"
        video_dic = {}

        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }

            if suffix == ".mp3":
                video_dic["type"] = "audio"
            elif suffix == ".mp4":
                video_dic["type"] = "video"

        return video_dic

    def get_like_count(self, response) -> int:
        like_count = 0
        like_url = "https://sputniknews.cn/services/dynamics/" + response.url.split("/")[-2] + "/" + \
                   response.url.split("/")[-1] + "?endless=1"
        headers = {
            "user-agent": "ozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        }
        res = requests.get(like_url, headers=headers)
        if res.status_code == 200:
            tree = Selector(res.text)
            like_count_str = tree.xpath("//span[@class='m-value']/text()").get()
            if like_count_str:
                like_count = int(like_count_str)
        return like_count

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
