# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class JpJfssParser(BaseParser):
    name = 'jfss'
    
    # 站点id
    site_id = "d5b6877f-19e4-4fb2-b20b-c59c9b725d1e"
    # 站点名
    site_name = "日本战略研究论坛"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "d5b6877f-19e4-4fb2-b20b-c59c9b725d1e", "source_name": "日本战略研究论坛", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8c4956-fe6f-11ec-a30b-d4619d029786", "会议记录", "http://www.jfss.gr.jp/key_note_chat", "政治"),
            ("4a8c48e8-fe6f-11ec-a30b-d4619d029786", "季度报告", "http://www.jfss.gr.jp/quarterly_report", "政治"),
            ("4a8c4802-fe6f-11ec-a30b-d4619d029786", "情报", "http://www.jfss.gr.jp/?page=1", "政治"),
            ("4a8c4870-fe6f-11ec-a30b-d4619d029786", "研究", "http://www.jfss.gr.jp/investigation", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.pub_time = {}
        self.title = {}
        self.tags = {}

    def wareki_year_exchange(self, year_str, year_num):
        try:
            value_gengou = year_str
            value_year = int(year_num)
            if value_gengou == '明治' and value_year < 46:
                result = value_year + 1867
            elif value_gengou == '大正' and value_year < 16:
                result = value_year + 1911
            elif value_gengou == '昭和' and value_year < 65:
                result = value_year + 1925
            elif value_gengou == '平成' and value_year < 32:
                result = value_year + 1988
            elif value_gengou == '令和':
                result = value_year + 2018
            else:
                result = None
        except ValueError:
            result = None
        return result

    def parse_list(self, response) -> list:
        if "quarterly_report" in response.url:
            news_urls = response.xpath('//div[@class="container"]//td/a/@href').extract()
            if news_urls:
                for url in list(set(news_urls)):
                    yield urljoin(response.url, url)
        if "investigation" in response.url:
            news_urls = response.xpath('//tr[@style="width: 25%;"]')
            if news_urls:
                for url in list(set(news_urls)):
                    url1 = urljoin(response.url, url.xpath('./td//a/@href').extract_first())
                    pubtime = ''.join(url.xpath('./td/h1/text()').extract_first().strip())
                    year_str = pubtime[:2]
                    year_num = re.findall('\d+', pubtime)[0]
                    pubtime = str(self.wareki_year_exchange(year_str, year_num)) + '-01-01'
                    title = ""
                    if '.pdf' in url1:
                        title = ''.join(url.xpath('./td[2]/a/text()').extract_first()).strip()
                    self.title[url1] = title
                    self.pub_time[url1] = pubtime
                    yield url1
        if "page" in response.url:
            news_urls = response.xpath('//div[@class="post-body"]/header')
            if news_urls:
                for news_url in list(set(news_urls)):
                    url = urljoin(response.url, news_url.xpath("./h3/a/@href").extract_first())
                    pub = news_url.xpath('./span[@class="post-meta-comments"]//text()').extract_first()
                    tag = news_url.xpath('./span[@post-meta-author]//text()').extract_first()
                    self.pub_time[url] = pub
                    self.tags[url] = tag
                    yield url
        if "key_note_chat" in response.url:
            news_urls = response.xpath('//a[@class="btn"]/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = self.title.get(response.url)
        if not title:
            title = response.xpath('//h1/text()|//div[@class="grid_12"]/h2/text()|//title/text()').extract_first(
                default="")
            if not title:
                title = ""
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = self.pub_time.get(response.url)
        if not time_:
            time_ = response.xpath('//meta[@name="pubdate"]/@content').extract_first()
            if time_:
                pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
            else:
                return "9999-01-01 00:00:00"
        else:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        if ".pdf" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
        else:
            news_tags = response.xpath('//div[@class="grid_12"]/h2/p|'
                                       '//div[@class="grid_12"]/div|'
                                       '//div[@class="grid_12"]/span/*|'
                                       '//div[@class="grid_12"]/h2/div')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                        if news_tag.xpath('.//img'):
                            con_img = self.parse_img(response, news_tag)
                            if con_img:
                                content.extend(con_img)
                        file = news_tag.xpath('./a/@href').extract_first()
                        if file:
                            if "pdf" in file:
                                file = self.parse_file(response, news_tag)
                                if file:
                                    content.append(file)
                        if news_tag.root.tag == "div":
                            if news_tag.xpath('./div').extract():
                                for con in news_tag.xpath('./div'):
                                    text_dict = self.parseOnetext(con)
                                    if text_dict:
                                        content.extend(text_dict)
                            else:
                                text_dict = self.parseOnetext(news_tag)
                                if text_dict:
                                    content.extend(text_dict)
                        else:
                            text_dict = self.parseOnetext(news_tag)
                            if text_dict:
                                content.extend(text_dict)

        return content

    def get_detected_lang(self, response) -> str:
        return "ja"

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
        imgs = news_tag.xpath('.//img/@src').extract()
        if imgs:
            img_list = []
            for img in imgs:
                if img:
                    img_url = urljoin(response.url, img)
                    dic = {"type": "image",
                           "name": news_tag.attrib.get('title', None),
                           "md5src": self.get_md5_value(img_url) + '.jpg',
                           "description": "".join(news_tag.xpath('.//figcaption//text()').extract()).strip(),
                           "src": img_url
                           }
                    img_list.append(dic)
            return img_list

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath("./a/@href").extract()
        if fileUrl:
            for file in fileUrl:
                file_src = urljoin(response.url, file)
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
