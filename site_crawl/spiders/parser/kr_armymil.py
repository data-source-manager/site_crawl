# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class KrarmymilParser(BaseParser):
    name = 'krarmymil'
    
    # 站点id
    site_id = "eb288286-36ce-431d-a5af-4027024a1754"
    # 站点名
    site_name = "韩国陆军"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "eb288286-36ce-431d-a5af-4027024a1754", "source_name": "韩国陆军", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("d7d98134-a346-433c-9651-3aee04db6c86", "新闻稿", "https://www.army.mil.kr/webapp/user/indexSub.do?codyMenuSeq=20360841&siteId=army", "政治"),
            ("8197f17a-de1c-463a-be4f-5b9095aefeea", "陆军新闻", "https://www.army.mil.kr/webapp/user/indexSub.do?codyMenuSeq=213347&siteId=army", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        if response.url.startswith('https://www.army.mil.kr/webapp/user/indexSub.do?codyMenuSeq=20360841&siteId=army'):
            urls = response.xpath('//td[@class="title"]/a/@href').extract() or ""
            for url in urls:
                yield urljoin(response.url, url)
        js_code = response.xpath('//div[@class="thumb"]/a/@onclick').extract() or ""
        for item in js_code:
            item = eval(item.replace('javascript:jf_view', '').replace(';', ''))
            boardId, boardSeq = item[1], item[2]
            news_url = response.url + f'&dum=dum&boardId={boardId}&page=1&command=albumView&boardSeq={boardSeq}&chkBoxSeq=&categoryId=&categoryDepth='
            yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//dl[@class="viewdata"]/dt/text()').extract_first(default="") or ""
        news_issue_title = title.strip().replace('\n', '').replace('\t', '')
        return news_issue_title or ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.xpath('//div[@class="id"]/dl/dt[contains(text(), "작성일")]/following-sibling::dd[1]/text()|'
                               '//div[@class="id"]/dl/dt[contains(text(), "일 자")]/following-sibling::dd[1]/text()').extract_first() or ""
        if time_:
            return str(datetime.strptime('20' + time_, "%Y.%m.%d %H:%M:%S"))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('//div[@id="divView"]|'
                                   '//div[@id="divView"]//img|'
                                   '//dl[@class="viewdata"]//dd[@class="file"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", "li", "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == 'dd':
                    file_dict = self.parse_file(response, news_tag)
                    if file_dict:
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
        file_src = urljoin('https://www.army.mil.kr/', news_tag.xpath(".//a/@href").extract_first())
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
