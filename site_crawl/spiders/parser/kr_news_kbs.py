# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

import requests

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class KR_news_kbsParser(BaseParser):
    name = 'kr_news_kbs'
    
    # 站点id
    site_id = "5aa58594-c2fb-46b2-88d4-dbcb8f81b91b"
    # 站点名
    site_name = "KBS新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "5aa58594-c2fb-46b2-88d4-dbcb8f81b91b", "source_name": "KBS新闻", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91234dd6-2f72-11ed-a768-d4619d029786", "国际", "https://news.kbs.co.kr/news/list.do?ctcd=0006&ref=pMenu#20220731&1", "政治"),
            ("91234da4-2f72-11ed-a768-d4619d029786", "政治", "https://news.kbs.co.kr/news/list.do?ctcd=0003&ref=pMenu#20220731&2", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        }
        now_time = time.strftime('%Y%m%d', time.localtime())
        params = {
            'currentPageNo': '1',
            'rowsPerPage': '12',
            'exceptPhotoYn': 'Y',
            'datetimeBegin': '{}000000'.format(now_time),
            'datetimeEnd': '{}235959'.format(now_time),
            'contentsCode': '',
            'localCode': '00',
        }
        if "0006" in response.url:
            params['contentsCode'] = '0006'
        if "0003" in response.url:
            params['contentsCode'] = '0003'
        post_url = "https://news.kbs.co.kr/api/getNewsList"
        res = requests.post(post_url, headers=headers, data=params).json()
        exmaple_url = 'https://news.kbs.co.kr/news/view.do?ncd={}'
        for data in res['data']:
            newsCode = data['newsCode']
            news_url = exmaple_url.format(newsCode)
            yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h5[@class='tit-s']/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        authors = response.xpath("//ul[@id='ulReporterList']/li/p[@class='name']/span[1]/text()").getall()
        if authors:
            for author_a in authors:
                author_list.append(author_a.replace("기자", "").strip())
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        times_ = response.xpath('//em[@class="date"][1]/text()').extract_first()
        time_ = times_.replace("입력", "").replace('(', '').replace(')', '')
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time - 60 * 60)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@id='cont_newstext']/node()|//div[@class='view_con_img']//img|/div[@id='cont_newstext']/div[contains(@style,'background-color')]/node()")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_data = news_tag.root.replace("\r\n", "").strip()
                        if text_data:
                            text_dict = {"data": text_data, "type": "text"}
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
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

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@src').extract_first()

        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": None,
                   "src": urljoin(response.url, news_tag.attrib.get('src'))}
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
        like_count_str = response.xpath("//span[@id='like_cnt']/text()").get()
        if like_count_str:
            like_count = int(like_count_str)
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        comment_count_str = response.xpath("//span[@id='reply_cnt']/text()").get()
        if comment_count_str:
            comment_count = int(comment_count_str)
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        return 0

    def get_if_repost(self, response) -> bool:
        if self.Dict[response.url].get("report"):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        resource_str = response.xpath("//span[@class='source']/a[@class='cate']/text()").get()
        if resource_str:
            repost_source = resource_str
            self.Dict[response.url] = {"report": True}

        return repost_source
