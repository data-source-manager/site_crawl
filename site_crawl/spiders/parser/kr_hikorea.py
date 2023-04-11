# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

import requests

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_hikoreaParser(BaseParser):
    name = 'kr_hikorea'
    
    # 站点id
    site_id = "d44fc06a-4502-38e1-964b-e99d8dd22a1b"
    # 站点名
    site_name = "你好韩国"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "d44fc06a-4502-38e1-964b-e99d8dd22a1b", "source_name": "你好韩国", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("6f4aaa28-ddcd-7d77-79b9-54bfab6e28fa", "资料室", "https://www.hikorea.go.kr/board/BoardDataListR.pt?page=1", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//tr[@class='board_line']")
        if news_urls:
            for extrat in news_urls:
                news_url = extrat.xpath("./td[3]/a/@onclick").get()
                times = extrat.xpath("./td[@class='tac'][4]/text()").get()
                NTCCTT_SEQ = re.findall("boardDetailR\(\'(.*?)\'\)", news_url)[0]
                post_url = 'https://www.hikorea.go.kr/board/BoardDetailR.pt'
                data = {
                    'page': '1',
                    'BBS_SEQ': '5',
                    'BBS_GB_CD': 'BS10',
                    'BBS_SEQ_GB_CD': '',
                    'CATEGORY': 'TITLE',
                    'SEARCHMESSAGE': '',
                    'NTCCTT_SEQ': NTCCTT_SEQ,
                    'TRAN_TYPE': 'ComSubmit',
                }
                res = requests.post(post_url, data=data, allow_redirects=False)
                rsp_url = res.headers['Location']
                self.Dict[rsp_url] = times
                yield rsp_url

    def get_title(self, response) -> str:
        title = response.xpath("//*[text()[contains(.,'제목')]]/following-sibling::td/text()").extract_first(
            default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = self.Dict[response.url]
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//form[@id='updateForm']//tr/td[@colspan='2']/node()")
        node_a = response.xpath("//th[@class='tdLabel']/following-sibling::td[1]/a")
        for sel in node_a:
            Params_str = sel.xpath("./@onclick").get()
            name = sel.xpath("./text()").get()
            apndFileNm, oriFileNm, NTCCTT_SEQ, APND_SEQ = \
            re.findall("fnNewFileDownLoad\('pt','ntc',\'(.*?)\', \'(.*?)\',\'(.*?)\','5','BS10',\'(.*?)\','NORMAL'\); ",
                       Params_str)[0]

            url = f"https://www.hikorea.go.kr/fileNewExistsChkAjax.pt?spec=pt&dir=ntc&apndFileNm={apndFileNm}&oriFileNm={oriFileNm}&BBS_GB_CD=BS10&BBS_SEQ=5&NTCCTT_SEQ={NTCCTT_SEQ}&APND_SEQ={APND_SEQ}&BBS_SKIN=NORMAL&TRAN_TYPE=ComSubmit"
            # pdf的获取post请求
            file_dic = {
                "type": "file",
                "src": url,
                "name": name or None,
                "description": None,
                "md5src": self.get_md5_value(url) + ".pdf"
            }
            content.append(file_dic)

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
        pdf_files = response.xpath("//dl[@class='artclForm']/dd[@class='artclInsert fileList']/ul/li")
        for pdf in pdf_files:
            pdf_file = pdf.xpath("./a/@href").get()
            name = pdf.xpath("./a/text()").get()
            if pdf_file:
                file_dic = {
                    "type": "file",
                    "src": urljoin(response.url, pdf_file),
                    "name": name or None,
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
        read_count_str = response.xpath("//div[@class='infor']/dl[2]/dd/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
