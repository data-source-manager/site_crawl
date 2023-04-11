# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class USA_usmaParser(BaseParser):
    name = 'usma'
    
    # 站点id
    site_id = "7f68fc11-c912-4efc-8217-d7618477443c"
    # 站点名
    site_name = "西点军校数字图书馆"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7f68fc11-c912-4efc-8217-d7618477443c", "source_name": "西点军校数字图书馆", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9123009c-2f72-11ed-a768-d4619d029786", "出版物", "http://digital-library.usma.edu/digital/api/collections?startPage=1&count=10", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.DICT1 = {}

    def parse_list(self, response) -> list:
        json_data = response.json()
        a_url = 'http://digital-library.usma.edu/digital/api/collections/{}'
        for cards in json_data['cards']:
            news_urls = a_url.format(cards['alias']).strip()
            self.DICT1[news_urls] = cards['title']
            yield news_urls

    def get_title(self, response) -> str:
        return self.DICT1[response.url]

    def get_author(self, response) -> list:
        pass

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.xpath('//span[@property="dc:date"]/@content').extract_first() or ""
        if time_:
            return str(datetime.strptime(time_.replace("T", " ").split("+")[0].strip(), "%Y %m %d  %H:%M:%S"))
        else:
            return "9999-01-01 00:00:00"
        # if time_:
        #     news_issue_time =
        #     pub_time = self.get_timestamp_by_datetime(news_issue_time)
        # else:
        #     pub_time = self.get_now_timestamp()
        # return datetime_helper.fuzzy_parse_timestamp(time_)

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        data = response.json()
        print(data)
        if data.get("pageText"):
            pageText = data['pageText']
            content.append(self.parse_text(pageText))
        if data.get("landingPageImage"):
            img_dict = self.parse_img(response, data["landingPageImage"]['mediumImagePath'])
            content.append(img_dict)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        dic['data'] = news_tag
        dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag)
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": img_url}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url, news_tag.xpath("").extract_first())
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(video_src) + ".mp4"
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
