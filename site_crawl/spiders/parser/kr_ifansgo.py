# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_ifransgoParser(BaseParser):
    name = 'kr_ifansgo'
    
    # 站点id
    site_id = "89c4861f-c2b9-b55c-5596-ea4dd5ef16d8"
    # 站点名
    site_name = "韩国外交安保研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "89c4861f-c2b9-b55c-5596-ea4dd5ef16d8", "source_name": "韩国外交安保研究所", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f6144ddf-2703-3435-90df-4a1e8b40bbfa", "出版物", "", "政治"),
            ("4a8e0aa2-fe6f-11ec-a30b-d4619d029786", "出版物/中国情况", "https://www.ifans.go.kr/knda/ifans/kor/pblct/PblctList.do?menuCl=P14&pageIndex=1", "政治"),
            ("4a8e096c-fe6f-11ec-a30b-d4619d029786", "出版物/国际形势", "https://www.ifans.go.kr/knda/ifans/kor/pblct/PblctList.do?menuCl=P04&pageIndex=1", "政治"),
            ("4a8e0872-fe6f-11ec-a30b-d4619d029786", "出版物/政策研究", "https://www.ifans.go.kr/knda/ifans/kor/pblct/PblctList.do?menuCl=P03&pageIndex=1", "政治"),
            ("4a8e073c-fe6f-11ec-a30b-d4619d029786", "出版物/粉丝观点", "https://www.ifans.go.kr/knda/ifans/kor/pblct/PblctList.do?menuCl=P18&pageIndex=1", "政治"),
            ("4a8e0624-fe6f-11ec-a30b-d4619d029786", "出版物/重大国际问题分析", "https://www.ifans.go.kr/knda/ifans/kor/pblct/PblctList.do?menuCl=P01&pageIndex=1", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//ul[@class='board_list']/li/a/@onclick").extract() or []
        url_template = 'https://www.ifans.go.kr/knda/ifans/kor/pblct/PblctView.do?csrfPreventionSalt=null&pblctDtaSn={}&menuCl={}&clCode={}&koreanEngSe=KOR&pclCode=&chcodeId=&searchCondition=searchAll&searchKeyword=&pageIndex=1'
        if news_urls:
            for news_url in news_urls:
                sn, code = re.findall("fnCmdView\(\'(.*?)\',\'(.*?)\'\)", news_url)[0]
                yield url_template.format(sn, code, code)

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='sub_top_view con_in']/strong[@class='tit']/text()").extract_first(
            default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_a = response.xpath("//strong[@class='write']/text()").get()
        if author_a:
            authors.append(author_a.split(" ")[0])
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//span[@class='date']/em/text()").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str.replace(") ", ""))
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags_node = response.xpath("//span[@class='tag']/a/text()").getall()
        if tags_node:
            tags_list.extend(tags_node)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='editor board_con con_in']//span[contains(@style,'16px;')]/node()")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'span']:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    img_src = self.parse_img(response, news_tag, img_xpath="./@src", des_xpath="./@alt")
                    if img_src:
                        content.append(img_src)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        pdf_file = response.xpath("//dl[@class='board_file']/dd/a/@href").get()
        if pdf_file:
            file_dic = {
                "type": "file",
                "src": urljoin(response.url, pdf_file),
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(pdf_file) + ".pdf"
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
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
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
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
        read_count_str = response.xpath("//span[@class='look']/em/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
