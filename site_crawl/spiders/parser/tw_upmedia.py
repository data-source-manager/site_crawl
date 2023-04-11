# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class TwUpmediaParser(BaseParser):
    name = 'upmedia'
    
    # 站点id
    site_id = "be784d64-8cfd-4024-a46d-0fecb15af840"
    # 站点名
    site_name = "上报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "be784d64-8cfd-4024-a46d-0fecb15af840", "source_name": "上报", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8c608a-fe6f-11ec-a30b-d4619d029786", "乌克兰抗俄", "https://www.upmedia.mg/news_list.php?Type=231", "政治"),
            ("4a8c5fb8-fe6f-11ec-a30b-d4619d029786", "国际", "https://www.upmedia.mg/news_list.php?Type=3", "政治"),
            ("c74da3f0-4761-45d4-aa62-c2ec9fd71dfb", "国际/专题", "https://www.upmedia.mg/news_list.php?Type=119", "政治"),
            ("f4a1c244-5981-42f8-aa95-619b11e89f84", "国际/国际现场", "https://www.upmedia.mg/news_list.php?Type=121", "政治"),
            ("f966775c-d77e-48d8-8355-f780256af318", "国际/实事", "https://www.upmedia.mg/news_list.php?Type=118", "政治"),
            ("4a8c6026-fe6f-11ec-a30b-d4619d029786", "大家论坛", "https://www.upmedia.mg/news_list.php?Type=130", "政治"),
            ("9a65c464-bb8e-4047-8a66-acc08bbecbed", "焦点", "https://www.upmedia.mg/news_list.php?Type=24", "政治"),
            ("1174ef95-b353-45b0-8e3b-0251dc50d801", "焦点/军事", "https://www.upmedia.mg/news_list.php?Type=244", "政治"),
            ("1b79457c-8ac2-4185-97b7-246fa41aa7fa", "焦点/政治", "https://www.upmedia.mg/news_list.php?Type=27", "政治"),
            ("91e6f5f3-ba14-45f6-aed8-65e355cac330", "焦点/社会", "https://www.upmedia.mg/news_list.php?Type=242", "政治"),
            ("e9cadb4f-06a1-4572-9f91-2d086e740e0e", "焦点/财经", "https://www.upmedia.mg/news_list.php?Type=243", "政治"),
            ("4a8c5f4a-fe6f-11ec-a30b-d4619d029786", "评论", "https://www.upmedia.mg/news_list.php?Type=1", "政治"),
            ("4a8c5ed2-fe6f-11ec-a30b-d4619d029786", "调查", "https://www.upmedia.mg/news_list.php?Type=2", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = 'be784d64-8cfd-4024-a46d-0fecb15af840'

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="top-dl"]//dd/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@id="ArticleTitle"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//div[@class="author"]/a/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@name="pubdate"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@id="news-info"]/div[@class="tag"]/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="img"]')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//div[@id="news-info"]/div[@class="editor"][1]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)

                if news_tag.root.tag == "div":
                    div_class = news_tag.xpath('./@class').extract_first()
                    if div_class:
                        if "backaground" in div_class:
                            con_img = self.parse_img(response, news_tag)
                            if con_img:
                                content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "ko"

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
                   "description": "".join(news_tag.xpath('.//img//@alt').extract()).strip(),
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
        like = response.xpath('//div[@class="um_like"]/@caption').extract_first()
        return int(like) if like else 0

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
