# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class KR_mndgoParser(BaseParser):
    name = 'kr_mndgo'
    
    # 站点id
    site_id = "8ff18f10-86b3-4d9e-b067-551c0b90335c"
    # 站点名
    site_name = "韩国国防部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "8ff18f10-86b3-4d9e-b067-551c0b90335c", "source_name": "韩国国防部", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("10b0f91f-62bf-38d4-8691-48763fd3fbe7", "国防新闻", "", "政治"),
            ("4a8d5508-fe6f-11ec-a30b-d4619d029786", "国防新闻/ETC", "https://mnd.go.kr/cop/kookbang/kookbangIlboList.do?siteId=mnd&pageIndex=1&findType=&findWord=&categoryCode=dema0138&boardSeq=&startDate=&endDate=&id=mnd_020108000000", "政治"),
            ("4a8d506c-fe6f-11ec-a30b-d4619d029786", "国防新闻/军队", "https://mnd.go.kr/cop/kookbang/kookbangIlboList.do?siteId=mnd&pageIndex=1&findType=&findWord=&categoryCode=dema0004&boardSeq=&startDate=&endDate=&id=mnd_020102000000", "政治"),
            ("4a8d5184-fe6f-11ec-a30b-d4619d029786", "国防新闻/海军", "https://mnd.go.kr/cop/kookbang/kookbangIlboList.do?siteId=mnd&pageIndex=1&findType=&findWord=&categoryCode=dema0005&boardSeq=&startDate=&endDate=&id=mnd_020103000000", "政治"),
            ("4a8d529c-fe6f-11ec-a30b-d4619d029786", "国防新闻/空军", "https://mnd.go.kr/cop/kookbang/kookbangIlboList.do?siteId=mnd&pageIndex=1&findType=&findWord=&categoryCode=dema0006&boardSeq=&startDate=&endDate=&id=mnd_020104000000", "政治"),
            ("4a8d53d2-fe6f-11ec-a30b-d4619d029786", "国防新闻/韩美同盟友", "https://mnd.go.kr/cop/kookbang/kookbangIlboList.do?siteId=mnd&pageIndex=1&findType=&findWord=&categoryCode=dema0007&boardSeq=&startDate=&endDate=&id=mnd_020106000000", "政治"),
            ("57465a04-a119-11ed-9cf5-1094bbebe6dc", "国防消息", "", "政治"),
            ("01084233-fe6c-4c66-a0cd-83b928cf061b", "国防消息/国防外交合作", "https://www.mnd.go.kr/user/boardList.action?boardId=I_7308482&siteId=mnd&id=mnd_010800000000", "政治"),
            ("e2de1d74-da1e-5bb6-8893-f2a0fa43cffb", "国防消息/国防新闻", "https://www.mnd.go.kr/cop/kookbang/kookbangIlboList.do?handle=dema0003&siteId=mnd&id=mnd_020101000000", "政治"),
            ("917bf53f-1ca2-3e02-8d2a-bdb0f9a20548", "国防消息/新闻发布", "https://www.mnd.go.kr/user/newsInUserRecord.action?siteId=mnd&handle=I_669&id=mnd_020500000000", "政治"),
            ("4a8d5008-fe6f-11ec-a30b-d4619d029786", "国防部", "https://mnd.go.kr/cop/kookbang/kookbangIlboList.do?siteId=mnd&pageIndex=1&findType=&findWord=&categoryCode=dema0003&boardSeq=&startDate=&endDate=&id=mnd_020101000000", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "8ff18f10-86b3-4d9e-b067-551c0b90335c"
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "020500000000" in response.url:
            news_urls = response.xpath('//div[@class="title"]/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    newsseq = re.findall('newsSeq=I_(.*)&page', news_url)[0]
                    rsp_url = f"https://www.mnd.go.kr/user/newsInUserRecord.action?siteId=mnd&page=1&newsId=I_669&newsSeq=I_{newsseq}&command=view&id=mnd_020500000000&findStartDate=&findEndDate=&findType=title&findWord=&findOrganSeq="
                    yield rsp_url
        elif "010800000000" in response.url:
            news_urls = response.xpath('//div[@class="title"]/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)
        else:
            demos = response.xpath(
                "//div[@class='title']/a/@href").extract() or []
            if demos:
                id = response.url.split("&id=")[-1]
                for demo in demos:
                    categoryCode, boardSeq = re.findall("javascript:jf_view\(\'(.*?)\',\'(\d+)\'\);", demo)[0]
                    demo_url = f"https://mnd.go.kr/cop/kookbang/kookbangIlboView.do?siteId=mnd&pageIndex=1&findType=&findWord=&categoryCode={categoryCode}&boardSeq={boardSeq}&startDate=&endDate=&id={id}"
                    yield demo_url

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='wrap_title']/div[@class='title']/text()").get()
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        auhtor_str = response.xpath("//dl[@class='first floatL']/dd/text()").get()
        if auhtor_str:
            authors.append(auhtor_str)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//dl[@class='floatL']/dd/text()").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@id='article_tags']/span/a/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[@class='post_content']/node()|//div[@class='article_body_view']//table[@class='table_LSize']|"
            "//div[@class='article_body_view']/p|//div[@class='post_content']/div|"
            "//div[@class='wrap_file']//li[1]/a")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p", "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "table":
                    con_img = self.parse_img(response, news_tag, img_xpath=".//img/@src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)

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
                    new_cons.append(x.replace("\n", "").replace("\r", "").replace('\t', '').strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath='./@alt'):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("./@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = news_tag.xpath("./source/@src").extract_first()
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(video_src) + ".mp4"
        }
        return video_dic

    def get_like_count(self, response) -> int:
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        read_count_str = response.xpath("//dl[@class='last floatR']/dd/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
