# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class TwDppnffParser(BaseParser):
    name = 'dppnff'
    
    # 站点id
    site_id = "4f90334f-4ed8-4a54-8158-cfff163462af"
    # 站点名
    site_name = "民进党新境界智库"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "4f90334f-4ed8-4a54-8158-cfff163462af", "source_name": "民进党新境界智库", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("6239a125-7fae-3679-aff5-89f7bfaf09b4", "中国事务", "https://www.dppnff.tw/article_research.php?id=37", "政治"),
            ("b99ca3fd-d3ca-43c2-9b5c-39fbcf4498a1", "交通", "https://www.dppnff.tw/article_research.php?id=44", "政治"),
            ("b75230d9-0942-4439-b0e8-88a4ffa4ad00", "农业", "https://www.dppnff.tw/article_research.php?id=43", "政治"),
            ("6ca53625-810f-478f-822d-2122d83ec086", "劳动", "https://www.dppnff.tw/article_research.php?id=50", "政治"),
            ("82ed082b-499c-4135-9edb-422c17c9b981", "医疗保健", "https://www.dppnff.tw/article_research.php?id=51", "政治"),
            ("39dd2daf-17d8-4ba8-a160-c2fe7c839c03", "司法", "https://www.dppnff.tw/article_research.php?id=48", "政治"),
            ("7ea2a709-07d2-3412-90cc-f2365a923f5e", "国防", "https://www.dppnff.tw/article_research.php?id=38", "政治"),
            ("4a8caf36-fe6f-11ec-a30b-d4619d029786", "国际要闻", "https://www.dppnff.tw/list.php?subtype=%E5%9C%8B%E9%9A%9B%E8%A6%81%E8%81%9E", "政治"),
            ("e446f295-c913-454b-a47d-88922a46fea7", "土地与住宅", "https://www.dppnff.tw/article_research.php?id=45", "政治"),
            ("6cc41cf3-cc95-48fd-b0a3-06775f24f0fd", "地方自治", "https://www.dppnff.tw/article_research.php?id=57", "政治"),
            ("190eeccc-f37e-4522-9485-f223571b08ff", "外交", "https://www.dppnff.tw/article_research.php?id=39", "政治"),
            ("ddb68e12-790b-41a7-90c6-70849df3d492", "好文推荐", "https://www.dppnff.tw/list.php?subtype=%E5%A5%BD%E6%96%87%E6%8E%A8%E8%96%A6", "政治"),
            ("7391949f-5d58-445e-a92e-627dce3c85a1", "媒体与传播", "https://www.dppnff.tw/article_research.php?id=54", "政治"),
            ("6235f479-0b69-4a1d-8eed-96f1d9fadb23", "性别", "https://www.dppnff.tw/article_research.php?id=56", "政治"),
            ("bd432468-4a03-4874-8ce2-42ef1fa88840", "教育", "https://www.dppnff.tw/article_research.php?id=52", "政治"),
            ("44f6346d-c23e-45b9-83e7-db38e51dfff3", "文化", "https://www.dppnff.tw/article_research.php?id=53", "政治"),
            ("c3ef288b-4277-4735-9aa8-94b262ed136b", "族群关系", "https://www.dppnff.tw/article_research.php?id=55", "政治"),
            ("4a8cad9c-fe6f-11ec-a30b-d4619d029786", "最新消息", "https://www.dppnff.tw/list.php?subtype=%E6%9C%80%E6%96%B0%E6%B6%88%E6%81%AF", "政治"),
            ("84a0b49f-8839-4ae1-9cee-341fe303e564", "民主专政", "https://www.dppnff.tw/article_research.php?id=58", "政治"),
            ("11a7f03f-aae8-4500-8f38-1b34f735a1b0", "环保", "https://www.dppnff.tw/article_research.php?id=46", "政治"),
            ("2b3539dd-9b26-4603-b0db-bfe89ab139ce", "社会福利", "https://www.dppnff.tw/article_research.php?id=49", "政治"),
            ("348dda23-99c6-424c-b1be-c2bed549f208", "科技", "https://www.dppnff.tw/article_research.php?id=47", "政治"),
            ("197ca8a4-5784-48f4-b31b-ff9b289f9aaa", "经济与产业", "https://www.dppnff.tw/article_research.php?id=41", "政治"),
            ("fa5207ef-725c-45e4-98e1-f816b1a45c60", "行政效能", "https://www.dppnff.tw/article_research.php?id=40", "政治"),
            ("4a8caeb4-fe6f-11ec-a30b-d4619d029786", "观点与评论", "https://www.dppnff.tw/list_comment.php?subtype=%E8%A7%80%E9%BB%9E%E8%88%87%E8%A9%95%E8%AB%96", "政治"),
            ("ecbed403-e31a-4178-91a0-d58035c5f6e8", "论坛活动", "https://www.dppnff.tw/list_event.php", "政治"),
            ("bfe30eb7-a9c0-44ec-b24e-b5457a5c7015", "财政与金融", "https://www.dppnff.tw/article_research.php?id=42", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "3d764140-3960-40cd-9425-8219b3199597"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="list_box"]/a/@href'
                                   '|//div[@class="research_box"]/h3/a/@href'
                                   '|//div[@class="list_box"]/h3/a/@href'
                                   '|//div[@class="list_event"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h3/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[@class="date"]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="article_box"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    con_file = news_tag.xpath("./a/@href").extract_first()
                    if con_file:
                        if "pdf" in con_file:
                            con_file = self.parse_file(response, news_tag)
                            if con_file:
                                content.append(con_file)
                    con_img = news_tag.xpath('./input/@src|'
                                             './img/@src').extract_first()
                    if con_img:
                        img = self.parse_img(response, news_tag)
                        if img:
                            content.append(img)
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-tw"

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
        img = news_tag.xpath('.//img/@src|'
                             './/input/@src').extract_first()
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
        fileUrl = news_tag.xpath("./a/@href").extract_first()
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
