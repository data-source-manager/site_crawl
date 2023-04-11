# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from .base_parser import BaseParser


class CNICParser(BaseParser):
    name = 'cnic'
    
    # 站点id
    site_id = "dc98c171-58cc-4e13-a564-694376bfaa57"
    # 站点名
    site_name = "贝尔沃堡军事基地"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "dc98c171-58cc-4e13-a564-694376bfaa57", "source_name": "贝尔沃堡军事基地", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("912319ce-2f72-11ed-a768-d4619d029786", "消息", "https://www.cnic.navy.mil/News", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//a[h1]/@href").extract() or ""
        if news_urls:
            for index, news_url in enumerate(news_urls):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_urls)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="content-wrap"]/h1/text()').extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        author = response.xpath('//div[@class="content-wrap"]/h2/text()').extract()
        return author

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.xpath('//div[@class="content-wrap"]/h1/following-sibling::div[1]/text()').extract_first() or ""
        if time_:
            return str(datetime.strptime(time_.strip(), "%d %B %Y"))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath('//div[@class="press-briefing__summary"]|'
                                   '//div[@class="acontent-container"]//p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "img":
                    img_dict = self.parse_img(response, news_tag)
                    content.append(img_dict)
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", "li", "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
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
