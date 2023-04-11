# -*- coding: utf-8 -*-
import re
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_kidareParser(BaseParser):
    name = 'kr_kidare'
    
    # 站点id
    site_id = "ed25a1cb-2bce-4a7a-9519-125b9c4d5130"
    # 站点名
    site_name = "韩国国防研究院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "ed25a1cb-2bce-4a7a-9519-125b9c4d5130", "source_name": "韩国国防研究院", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f311a6fe-b627-0e5a-20e7-ef8f68aaee61", "专题", "", "政治"),
            ("91233c38-2f72-11ed-a768-d4619d029786", "专题/东亚研究", "https://www.kida.re.kr/frt/board/frtNormalBoard.do?sidx=2184&depth=2", "政治"),
            ("91233c6a-2f72-11ed-a768-d4619d029786", "媒体", "https://www.kida.re.kr/frt/board/frtKidaMediaBoard.do?sidx=1829&depth=3", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "frtNormalBoard" in response.url:
            format_url = 'https://www.kida.re.kr/frt/board/frtNormalBoardDetail.do?sidx=2184&idx={}&depth=2&searchCondition=&searchKeyword=&pageIndex=1&lang=kr'
            news_urls = response.xpath(
                "//td[@class='alignl subject']/a/@onclick").extract() or []
            news_urls = [format_url.format(re.findall("goDetail\((.*?)\)", new_url)[0]) for new_url in news_urls]
        elif "frtKidaMediaBoard" in response.url:
            news_urls = response.xpath(
                "//strong[@class='title']/a/@onclick").extract() or []
            news_urls = [re.findall("goKidaMedia\('.*?','(.*?)'\)", new_url)[0] for new_url in news_urls]
        else:
            news_urls = []
        print(news_urls)
        if news_urls:
            for news_url in news_urls:
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath(
            "//meta[@name='title']/@content|//div[@class='table_area']/table[@class='view']//tr[1]/td/text()").extract_first(
            default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        Author_str = response.xpath("//div[@class='table_area']/table[@class='view']//tr[2]/td/text()").extract_first()
        if Author_str:
            authors.append(Author_str.replace("\r\n", "").strip())
        return authors

    def get_pub_time(self, response) -> str:
        if "sidx=2184" in response.url:
            pub = response.xpath(
                "//*[text()[contains(.,'발행일자')]]/following-sibling::td/text()[normalize-space()]").extract_first()
            if pub:
                pub = str(datetime_helper.fuzzy_parse_datetime(pub.replace(".", "-")))
                return pub
        else:
            html = response.text
            dateText = re.findall('"dateText":{"simpleText":"(.*?)"}}},', html)
            if dateText:
                pub = dateText[0]
                if pub:
                    pub = str(datetime_helper.fuzzy_parse_datetime(pub))
                    return pub
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 提升作用域
        if "youtube" in response.url:
            video_dic = {
                "type": "video",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".mp4"
            }
            content.append(video_dic)
            return content
        news_tags = response.xpath("//div[@class='table_area']/table[@class='view']//tr/td[@colspan='2']/*")
        pdf_file = response.xpath("//ul[@class='file_list']/li/a/@onclick").get()
        if pdf_file:
            pdf_href = "https://www.kida.re.kr/" + re.findall("location.href='(.*?)'", pdf_file)[0]
            file_dic = {
                "type": "file",
                "src": pdf_href,
                "name": response.xpath("//ul[@class='file_list']/li/a/text()").extract_first().replace("\r\n",
                                                                                                       "").strip(),
                "description": None,
                "md5src": self.get_md5_value(pdf_href) + ".pdf"
            }
            content.append(file_dic)
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", 'h5', "strong", "p"]:
                    if news_tag.xpath(".//img"):
                        img_dict = self.parse_img(response, news_tag)
                        content.append(img_dict)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
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
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag):
        img_url = urljoin(response.url, news_tag.attrib.get('src'))
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": response.xpath(".//p/text()").extract_first(),
               "src": img_url
               }
        return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath(".//a/text()").extract_first(),
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
        read_count = 0
        if "youtube" in response.url:
            html = response.text
            viewCount = re.findall('"viewCount":"(.*?)","author"', html)
            if viewCount:
                read_count = int(viewCount[0])
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
