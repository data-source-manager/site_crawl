# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from lxml import etree

from .base_parser import BaseParser


class CecgovParser(BaseParser):
    name = 'cecgov'
    
    # 站点id
    site_id = "78230650-f33f-4c37-b16a-5448e0cc8338"
    # 站点名
    site_name = "中央选举委员员"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "78230650-f33f-4c37-b16a-5448e0cc8338", "source_name": "中央选举委员员", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("161e6d65-628e-34ad-9eb1-7c1611f62db5", "公民投票", "", "政治"),
            ("912315d2-2f72-11ed-a768-d4619d029786", "公民投票/最新消息", "https://web.cec.gov.tw/referendum/cmsList/news?order=asc&offset=0&limit=10&begin=&end=&title=", "政治"),
            ("9123156e-2f72-11ed-a768-d4619d029786", "新闻稿", "https://www.cec.gov.tw/central/cmsList/111news?order=asc&offset=0&limit=10&begin=&end=&title=", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        for item in response.json():
            contentId = str(item['contentId'])
            if response.url.startswith('https://www.cec.gov.tw/central'):
                new_url = 'https://www.cec.gov.tw/central/cmsData/111news/' + contentId
            else:
                new_url = 'https://web.cec.gov.tw/referendum/cmsData/news/' + contentId
            yield new_url

    def get_title(self, response) -> str:
        json_data = response.json()
        title = json_data['content']['title']
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        json_data = response.json()
        time_ = json_data['content']['createDate']
        if time_:
            return str(datetime.fromtimestamp(time_ / 1000))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        html = etree.HTML(response.json()['content']['content'])
        if html:
            cons = html.xpath('//text()')
            new_cons = ''
            for x in cons:
                if x.strip():
                    new_cons += x.strip()
            content.append({'data': new_cons, 'type': 'text'})

            tables = html.xpath('//table')
            for table in tables:
                content.append({'data': etree.tostring(table).decode(), 'type': 'text'})

        file_tags = response.json()['files']
        if file_tags:
            for tag in file_tags:
                file_dict = self.parse_file(response, tag)
                content.append(file_dict)

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
               "name": news_tag.attrib.get('title'),
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('alt'),
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin('https://web.cec.gov.tw/', news_tag['fullFileUrl'])
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag['fullFileName'],
            "description": news_tag['filenameSearch'],
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
        json_data = response.json()
        read_count = json_data['hitsCount'] or ''
        if read_count:
            return int(read_count)
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
