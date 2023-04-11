# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    站点解析模版
"""


class TW_pchomeParser(BaseParser):
    name = 'tw_pchome'
    
    # 站点id
    site_id = "17e00367-6e83-4717-9f4e-b0505da0fbde"
    # 站点名
    site_name = "Pchome新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "17e00367-6e83-4717-9f4e-b0505da0fbde", "source_name": "Pchome新闻", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("02de070f-0a49-3d7a-95ab-cf72901ff3a2", "国际", "", "政治"),
            ("4a8cc624-fe6f-11ec-a30b-d4619d029786", "国际/最新国际新闻", "https://news.pchome.com.tw/cat/internation/1", "政治"),
            ("c588f356-0722-386e-bf43-0c56d683f9aa", "政府", "", "政治"),
            ("4a8cc570-fe6f-11ec-a30b-d4619d029786", "政府/最新政府消息新闻", "https://news.pchome.com.tw/cat/public/1", "政治"),
            ("26e6eb9e-b2ff-3a2b-8a84-36247d3af6a1", "政治", "", "政治"),
            ("4a8cc4bc-fe6f-11ec-a30b-d4619d029786", "政治/最新政治新闻", "https://news.pchome.com.tw/cat/politics/1", "政治"),
            ("efe28926-3750-3c97-9441-887ba6c566b8", "科技", "", "政治"),
            ("4a8cc78c-fe6f-11ec-a30b-d4619d029786", "科技/最新科技新闻", "https://news.pchome.com.tw/cat/science", "政治"),
            ("5fac2d3a-a50e-3e9b-91af-cf4f9da4f7a8", "财经", "", "政治"),
            ("4a8cc6e2-fe6f-11ec-a30b-d4619d029786", "财经/最新财经新闻", "https://news.pchome.com.tw/cat/finance/1", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="channel_newssection"]/p[1]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//p[@class="article_title"]/@title').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//time[@pubdate]/@pubdate').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@calss="article_text"]|//div[@calss="article_text"]/img')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
