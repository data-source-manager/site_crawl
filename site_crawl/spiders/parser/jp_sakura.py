# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class JP_sakuraParser(BaseParser):
    name = 'jp_sakura'
    
    # 站点id
    site_id = "1c06a822-7e5a-44f6-ae18-df89cc0d8b99"
    # 站点名
    site_name = "海上自卫队"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "1c06a822-7e5a-44f6-ae18-df89cc0d8b99", "source_name": "海上自卫队", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8ea5fc-fe6f-11ec-a30b-d4619d029786", "图片集", "http://j-navy.sakura.ne.jp/special-top2.html", "政治"),
            ("4a8ea5ca-fe6f-11ec-a30b-d4619d029786", "资料室", "http://j-navy.sakura.ne.jp/file-top2.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "file-top2" in response.url:
            news_nodes = response.xpath('//table//tr')
            if news_nodes:
                for news_node in news_nodes:
                    rep_url = news_node.xpath('./td/font[2]/a/@href').get()
                    rep_time = news_node.xpath('./td[2]//text()').get()
                    url_ = urljoin(response.url, rep_url)
                    self.Dict[url_] = {"time": rep_time}
                    yield url_
        else:
            news_items = response.xpath('//tbody/tr/td')
            if news_items:
                for news_item in news_items:
                    rsp_url = news_item.xpath('.//a/@href').get()
                    rsp_time = news_item.xpath('./font[@face="ＭＳ Ｐゴシック"]/text()[contains(.,"年")]').get()
                    url = urljoin(response.url, rsp_url)
                    self.Dict[url] = {"time": rsp_time}
                    yield url

    def get_title(self, response) -> str:
        title = response.xpath('//title/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        times = self.Dict[response.url]["time"]
        if times:
            try:
                time_ = re.findall('\d{4}年\d{1,2}月\d{1,2}', times)[0].replace("年", "-").replace("月", "-")
                if time_:
                    pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                    return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
            except:
                return "9999-01-01 00:00:00"

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//table//tr/td/node()|//table[@bgcolor="#cccccc"]')
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "font", "b"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                elif news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag == "table":
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
        img = news_tag.xpath('./@src').extract_first()
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
