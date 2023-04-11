# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class RU_globalaffairsParser(BaseParser):
    name = 'ru_globalaffairs'
    
    # 站点id
    site_id = "65f90673-af82-4fc2-b72f-365d0e42a330"
    # 站点名
    site_name = "俄罗斯全球政策杂志"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "65f90673-af82-4fc2-b72f-365d0e42a330", "source_name": "俄罗斯全球政策杂志", "direction": "ru", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("881cbcdd-1323-4590-9552-3e75874c7188", "事件", "", "政治"),
            ("ffb39b64-f438-450d-99b7-41f978cdf9cb", "事件/公告", "https://www.globalaffairs.ru/events/upcoming/", "政治"),
            ("e2c3e9a5-14db-400e-81f3-595e109a5614", "事件/结果", "https://www.globalaffairs.ru/events/posts/", "政治"),
            ("48d1f62f-8284-353a-85a7-33fefec9631c", "分析", "", "政治"),
            ("4a8d1bf6-fe6f-11ec-a30b-d4619d029786", "分析/意见", "https://globalaffairs.ru/analytics/opinions/", "政治"),
            ("4a8d1a84-fe6f-11ec-a30b-d4619d029786", "分析/报告", "https://globalaffairs.ru/analytics/reports/", "政治"),
            ("4a8d1b24-fe6f-11ec-a30b-d4619d029786", "分析/评论", "https://globalaffairs.ru/analytics/reviews/", "政治"),
            ("4a8d19c6-fe6f-11ec-a30b-d4619d029786", "分析/采访", "https://globalaffairs.ru/analytics/interviews/", "政治"),
            ("30056ae9-1ee7-418c-8d81-0cbd61513168", "项目", "", "政治"),
            ("9d016b0e-1e52-4e99-8cb2-1b3e3cbdeb9f", "项目/CCEMI 变化分析", "https://globalaffairs.ru/tag/czkemi/", "政治"),
            ("cce73761-639f-4c90-bae9-894fef6e0799", "项目/博客", "https://globalaffairs.ru/projects/podcasts/", "政治"),
            ("da169a1a-e877-4b57-837d-0242224f2d52", "项目/学校“教科学家”", "https://globalaffairs.ru/projects/shkola-avtorov-uchi-uchyonogo/", "政治"),
            ("326a781b-3da3-40d9-bf97-bcc25be0c14d", "项目/电视杂志", "https://globalaffairs.ru/tag/mezhdunarodnoe-obozrenie/", "政治"),
            ("7da252df-9180-4b17-a6b1-b0db81ece961", "项目/行动指南", "https://globalaffairs.ru/tag/rukovodstvo-k-dejstviyu/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//div[@class='row']/div[@class='row__col col-xl-4 col-lg-4 col-md-4']/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='dk-cover__title']/text()").get()
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        auhtor_strs = response.xpath("//div[@class='dk-author__about']/a/text()").getall()
        if auhtor_strs:
            authors.extend(auhtor_strs)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='dk-cover__date']/text()").get()
        if Date_str:
            time_ = datetime.strptime(Date_str, "%d.%m.%Y")
            return datetime_helper.parseTimeWithOutTimeZone(time_, site_name="俄罗斯全球政策杂志")

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@class='dk-article__tags']/a[@class='dk-article__tags-item']/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            "//div[contains(@class,'dk-article__body')]/*|//div[@class='dk-article__quote-text']")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span",
                                           "p"] or "k-article__quote-text" in news_tag.root.get("class", ""):
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        file_src = response.xpath("//a[contains(@class,'dk-article__download')]/@href").get()
        if file_src:
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
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
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
