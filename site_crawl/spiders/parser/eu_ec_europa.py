# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class EcEuropaParser(BaseParser):
    name = 'ec_europa'
    
    # 站点id
    site_id = "e450f3a1-6054-4138-b540-edeb65f239a5"
    # 站点名
    site_name = "欧盟委员会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e450f3a1-6054-4138-b540-edeb65f239a5", "source_name": "欧盟委员会", "direction": "fr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91230cfe-2f72-11ed-a768-d4619d029786", "新闻稿", "https://ec.europa.eu/commission/presscorner/api/latestnews?language=en&ts=1658211245584&pagesize=10&pagenumber=1", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.json()
        for item in news_urls['docuLanguageListResources'][1:]:
            refCode = item['refCode']
            news_url = 'https://ec.europa.eu/commission/presscorner/api/documents?reference=' + refCode + '&language=en'
            yield news_url

    def get_title(self, response) -> str:
        title = response.json()['docuLanguageResource']['title']
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        author = []
        return author

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.json()['eventDate']
        if time_:
            return str(datetime.strptime(time_.strip(), "%Y-%m-%d"))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        json_data = response.json()
        text = json_data['docuLanguageResource']['htmlContent']
        content.append({'data': text, 'type': 'text'})
        if json_data['docuLanguageResource']['hasPdf']:
            pdf_url = '_'.join(json_data['refCd'].split('/'))
            pdf_url = f'https://ec.europa.eu/commission/presscorner/api/files/document/print/en/{pdf_url}/{pdf_url}_EN.pdf'
            file_dic = {
                "type": "file",
                "src": pdf_url,
                "name": json_data['docuLanguageResource']['subtitle'],
                "description": None,
                "md5src": self.get_md5_value(pdf_url) + ".pdf"
            }
            content.append(file_dic)

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
               "name": news_tag.attrib.get('title', None),
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": news_tag.attrib.get('alt'),
               "src": urljoin(response.url, news_tag.attrib.get('src'))}
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.attrib.get('title'),
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
