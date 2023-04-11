# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class USA_rfaorgburmeseParser(BaseParser):
    name = 'usa_rfaorgburmese'
    
    # 站点id
    site_id = "34d4e09d-1709-4dbb-b006-8b2a504c2736"
    # 站点名
    site_name = "自由亚洲电台缅甸网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "34d4e09d-1709-4dbb-b006-8b2a504c2736", "source_name": "自由亚洲电台缅甸网", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8ecbea-fe6f-11ec-a30b-d4619d029786", "新闻文章", "https://www.rfa.org/burmese/program_2/story_archive?uids=3a8fdc4af07647f18c6aaaf321d073d0@ec7c6de900114eacb5f2cfcf2cb17f47@0006d971528e47edaaba99b0f87d14f9@4a9fbd15c3394ea0895ddb4b3b12f9ed@5f80f427e88046aeb990adb39d04e7a6@08cc13ae3457477ba6afc235e5c88c3a@b693b2844672455eb8c6ac8f74eb9390@69098cb788074057849fda3f5e798afc@fbec173f08d342e58e9edc3d5798445c@9c16a5674cf1433b972d0667fbf499d5@5431b18810c84a47b7db0a1822e2b63c@77a0b86a25c0409abaa790261967081d@7911e459c3dd4dc6a16f8fe183ce84a6@26c2bce9028549e396bac40466aaafbf@de1e504e21a541038e8ba201455b753a", "政治"),
            ("4a8ecb86-fe6f-11ec-a30b-d4619d029786", "缅甸部", "https://www.rfa.org/burmese/story_archive?uids=710702a50046454b9ee724fcf55a02d0@26c2bce9028549e396bac40466aaafbf@3979d3cd277f4699b96b55112f71add2@f4444ff0df2e40b8ad7da740e9a12713@2f3e729457904d2b95b63a278b00eee6@11e9e42921724a3385483525c53d5112@7911e459c3dd4dc6a16f8fe183ce84a6@de1e504e21a541038e8ba201455b753a@74505830461c446f93cbb9e7d239087b@0b7e546ae2b74ff1ad89ce79d053679a@68b89474dfaa4d1cb7cdbff92ad9fd59@3a8fdc4af07647f18c6aaaf321d073d0@0a73c829d5724629b2bcae83cd8d146d@ec7c6de900114eacb5f2cfcf2cb17f47@b47a0efe1c6d40bea0935f0a6b9badb6@5b43202a3e0643a0816320f7ef33e337@7120365d3d814d24a1bb846f88ea2a47", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="sectionteaser archive"]/h2/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="mobilecontainer"]/h1/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//div[@id="dateline"]/span[@id="story_date"]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@id="headerimg"]/img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//div[@id="storytext"]/*')
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
        return "mm"

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
