# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

import requests
import urllib3

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.time_deal.translatetTime import twYearDict

"""
    站点解析模版
"""


class TwMndParser(BaseParser):
    name = 'mnd'
    
    # 站点id
    site_id = "42625a88-9cad-4c06-a78f-603c77fc3684"
    # 站点名
    site_name = "台湾国防部全球资讯网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "42625a88-9cad-4c06-a78f-603c77fc3684", "source_name": "台湾国防部全球资讯网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8beb96-fe6f-11ec-a30b-d4619d029786", "即时军事动态", "https://www.mnd.gov.tw/PublishTable.aspx?Types=%E5%8D%B3%E6%99%82%E8%BB%8D%E4%BA%8B%E5%8B%95%E6%85%8B&title=%E5%9C%8B%E9%98%B2%E6%B6%88%E6%81%AF", "政治"),
            ("4a8bec7c-fe6f-11ec-a30b-d4619d029786", "即时新闻澄清专区", "https://www.mnd.gov.tw/PublishTable.aspx?Types=%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E%E6%BE%84%E6%B8%85%E5%B0%88%E5%8D%80&title=%E5%9C%8B%E9%98%B2%E6%B6%88%E6%81%AF", "政治"),
            ("4a8bec04-fe6f-11ec-a30b-d4619d029786", "新闻稿", "https://www.mnd.gov.tw/PublishTabs.aspx?parentId=65&NodeId=657&title=%E5%9C%8B%E9%98%B2%E6%B6%88%E6%81%AF&SelectStyle=%E6%96%B0%E8%81%9E%E7%A8%BF", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.click_num = {}

    def get_detail_url(self, post_url: str, url_param: str, VIEWSTATE, EVENTVALIDATION):
        data = {
            "__EVENTTARGET": url_param,
            "__VIEWSTATE": VIEWSTATE,
            "__EVENTVALIDATION": EVENTVALIDATION
        }
        urllib3.util.url.FRAGMENT_CHARS |= {"%"}
        proxy = {
            "https": "http://127.0.0.1:9910",
            "http": "http://127.0.0.1:9910"
        }
        requests.packages.urllib3.disable_warnings()
        r = requests.Request('POST', post_url, data=data).prepare()
        r.url = post_url
        response = requests.Session().send(r, verify=False, timeout=10)
        return response.url

    def parse_list(self, response) -> list:
        post_url = urljoin(response.url, response.xpath("//form/@action").extract_first())
        view_state = response.xpath('//input[@id="__VIEWSTATE"]/@value').extract_first()
        event_valtdation = response.xpath('//input[@id="__EVENTVALIDATION"]/@value').extract_first()

        news_urls = response.xpath('//td[@class="w-90"]|//td[@class="w-80"]')
        if news_urls:
            for news_url in list(set(news_urls)):
                url_param = re.findall("__doPostBack\('(.*?)'", news_url.xpath("./a/@href").extract_first())
                click_num = re.findall("\d+", news_url.xpath("./span/text()").extract_first())[0]
                if url_param:
                    url = self.get_detail_url(post_url, url_param[0], view_state, event_valtdation).split("&")[0]
                    self.click_num[url] = click_num
                    yield urljoin(response.url, url)

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="titleContent"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//div[@class="date"]/span/text()').extract_first()
        if time_:
            time_split = time_.split("/")
            time_year = twYearDict.get(time_split[0].strip())
            time_ = f"{time_year}/{time_split[1]}/{time_split[2]}"
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="thisPages"]/*')
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

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        dic = {}
        if cons:
            if new_cons:
                dic['data'] = "".join(cons).strip()
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
            if img.startswith("data:image/gif;base64"):
                return {}
            if img.endswith(".gif"):
                return {}
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
        videoUrl = news_tag.xpath("./@src").extract_first()
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
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        return self.click_num[response.url]

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
