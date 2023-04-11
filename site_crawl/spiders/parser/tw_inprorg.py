# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TW_inprorgParser(BaseParser):
    name = 'tw_inprorg'
    
    # 站点id
    site_id = "f23f5bc1-4188-4e6d-9b22-8ee67683078a"
    # 站点名
    site_name = "财团法人国策研究院文教基金会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f23f5bc1-4188-4e6d-9b22-8ee67683078a", "source_name": "财团法人国策研究院文教基金会", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8e76d6-fe6f-11ec-a30b-d4619d029786", "国内议题", "http://www.inpr.org.tw/m/412-1728-111.php?Lang=zh-cn", "政治"),
            ("4a8e7744-fe6f-11ec-a30b-d4619d029786", "国际议题", "http://www.inpr.org.tw/m/412-1728-113.php?Lang=zh-cn", "政治"),
            ("4a8e7604-fe6f-11ec-a30b-d4619d029786", "座谈会", "http://www.inpr.org.tw/m/412-1728-101.php?Lang=zh-cn", "政治"),
            ("4a8e7672-fe6f-11ec-a30b-d4619d029786", "研讨会", "http://www.inpr.org.tw/m/412-1728-108.php?Lang=zh-cn", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_items = response.xpath('//div[@class="d-txt"]')
        if news_items:
            for news_item in news_items:
                rsp_url = news_item.xpath("./h5/a/@href").get()
                rsp_time = news_item.xpath("./div/i/text()").get()
                self.Dict[rsp_url] = {"time": rsp_time}
                yield urljoin(response.url, rsp_url)

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="mpgtitle"]/h3/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        # time_ = response.xpath('//div[@class="mdetail"]').extract_first()
        time_ = self.Dict[response.url]['time']
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="mcont"]/div//img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath(
            '//div[@class="mpgdetail"]/*|//div[@class="mpgdetail"]/div//span|//div[@class="mcont"]/div')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "div" and news_tag.root.get("class", "") == "mpgdetail":
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parse_text(con)
                        if con_text:
                            content.append(con_text)

                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

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
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": None,
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
