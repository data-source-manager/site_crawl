# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class AllhandsParser(BaseParser):
    name = 'allhands'
    
    # 站点id
    site_id = "30241959-2df9-4d4d-877c-60f60934fd9b"
    # 站点名
    site_name = "美国海军水手杂志"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "30241959-2df9-4d4d-877c-60f60934fd9b", "source_name": "美国海军水手杂志", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("6c30a99f-f2d2-3351-8a33-663137994f60", "媒体", "", "政治"),
            ("91231bae-2f72-11ed-a768-d4619d029786", "媒体/舰队档案", "https://allhands.navy.mil/DesktopModules/MediaCollectionList/MCLAPI.ashx?portalId=1&moduleId=1178&collectionId=18781", "军事"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.detail_article_info = {}

    def parse_list(self, response) -> list:
        res = response.json()
        files = res['Collections'][0]['Files']
        for file in files:
            file_url = file['FileProperties'][0]['ViewUrl']
            file_title = file['Title']
            file_ct = file['CreatedOn']
            file_desc = file['Description']
            detail_ur = f'http://httpbin.org/base64/allhands{file["CreatorId"]}.pdf'
            self.detail_article_info[detail_ur] = {
                "real_url": file_url,
                "file_title": file_title,
                "file_time": file_ct,
                "file_desc": file_desc
            }
            # 随便给个详情页地址
            yield {'origin_url': file_url,
                   'real_url': f'http://httpbin.org/base64/allhands{file["CreatorId"]}.pdf'}

    def get_title(self, response) -> str:
        return self.detail_article_info[response.url]["file_title"]

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = self.detail_article_info[response.url]["file_time"]
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = [self.parse_file(response, news_tag=None)]
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
            dic['data'] = new_cons
            dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": None,
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = self.detail_article_info[response.url]["real_url"]
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": "",
            "description": self.detail_article_info[response.url]["file_desc"],
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
