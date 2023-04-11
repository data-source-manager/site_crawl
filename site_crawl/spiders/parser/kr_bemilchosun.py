# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class KR_bemilchosunParser(BaseParser):
    name = 'kr_bemilchosun'
    
    # 站点id
    site_id = "36b90f68-5ced-4207-9c68-701bac7b1889"
    # 站点名
    site_name = "韩国军事论坛"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "36b90f68-5ced-4207-9c68-701bac7b1889", "source_name": "韩国军事论坛", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("70b3a4a9-c1ee-4686-a716-71e3538f1643", "专家角", "https://bemil.chosun.com/nbrd/bbs/list.html?b_bbs_id=10158", "政治"),
            ("fe25c11c-e0ab-40c9-aeb7-a6a12af07f69", "全球防务评论", "https://bemil.chosun.com/nbrd/bbs/list.html?b_bbs_id=10165", "政治"),
            ("b50f5af8-84dc-456e-a588-0f1156e1fc44", "国防日报", "https://bemil.chosun.com/nbrd/bbs/list.html?b_bbs_id=10002", "政治"),
            ("4a8eaba6-fe6f-11ec-a30b-d4619d029786", "新闻", "https://bemil.chosun.com/nbrd/bbs/newslist.html", "政治"),
            ("4a8eabd8-fe6f-11ec-a30b-d4619d029786", "朝鲜新闻", "https://bemil.chosun.com/svc/list/list.html?catid=91", "政治"),
            ("104d9809-9659-4622-8ea8-40af6660ee33", "武器新闻", "https://bemil.chosun.com/nbrd/bbs/list.html?b_bbs_id=10180", "政治"),
            ("4a8eac0a-fe6f-11ec-a30b-d4619d029786", "焦点", "https://bemil.chosun.com/nbrd/bbs/focus_section.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        if "catid=91" in response.url:
            news_urls = response.xpath('//div[@class="thumb_img"]/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)
        else:
            news_urls = response.xpath('//table[@class="BasicTables"]/tbody/tr/td[2]/a[1]/@onclick').extract() or ""
            tem_url = 'https://bemil.chosun.com/nbrd/bbs/view.html?b_bbs_id={}&branch=&pn=1&num={}'
            if news_urls:
                for news_url in news_urls:
                    url_info = re.findall("\d+", news_url)
                    if url_info and len(url_info) >= 3:
                        yield tem_url.format(url_info[0], url_info[2])

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="board_detail"]/div[@class="conSubject"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//div[@class="board_detail"]//div[@class="uname"]//a/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        times_ = response.xpath('//div[@class="board_detail"]//div[@class="wdate"]/text()').extract_first()
        if "html_dir" in response.url:
            time_ = re.findall('입력 : (.*)', times_)[0]
        else:
            time_ = re.findall('입력 (.*)', times_)[0]
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        if "html_dir" in response.url:
            news_tags = response.xpath(
                '//div[@class="board_body"]/*|//div[@class="board_body"]//img|//iframe[contains(@src,"naver")]')
        else:
            news_tags = response.xpath(
                '//div[@class="board_body"]/*|//div[@class="board_body"]//td[@class="view_img"]/img')
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
                if news_tag.root.tag == "iframe":
                    con_file = self.parse_media(response, news_tag, media_type="video")
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
            oneCons = "".join(cons).strip().replace('\t', '').replace('\r', '').replace('\n', '')
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
        read_count = 0
        read_count_str = response.xpath('//div[@class="board_detail"]//ul[@class="pipeline"]/li/text()').get()
        if read_count_str:
            read_count = int(re.findall('조회수 (.*)', read_count_str)[0])
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
