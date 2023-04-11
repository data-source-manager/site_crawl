# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class BN_brudirectParser(BaseParser):
    name = 'bn_brudirect'
    
    # 站点id
    site_id = "b391bbee-5ae8-44eb-8970-8c01d34b3616"
    # 站点名
    site_name = "文莱快线"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "b391bbee-5ae8-44eb-8970-8c01d34b3616", "source_name": "文莱快线", "direction": "bn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("1cc44170-824e-30bc-b87d-54a0bae33361", "世界", "", "政治"),
            ("4a8d4ee6-fe6f-11ec-a30b-d4619d029786", "世界/中东", "https://www.brudirect.com/viewall_world-middleeast.php", "政治"),
            ("4a8d4b8a-fe6f-11ec-a30b-d4619d029786", "世界/亚洲", "https://www.brudirect.com/viewall_world-asia.php", "政治"),
            ("4a8d4dd8-fe6f-11ec-a30b-d4619d029786", "世界/欧洲", "https://www.brudirect.com/viewall_world-europe.php", "政治"),
            ("4a8d4cc0-fe6f-11ec-a30b-d4619d029786", "世界/美国", "https://www.brudirect.com/viewall_world-america.php", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//td/p[@class='m_2'][4]/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//p[@class='m_1']/span/text()").get()
        return title.strip() or ""

    def get_author(self, response) -> list:
        authors = []
        auhtor_str = response.xpath("//dl[@class='first floatL']/dd/text()").get()
        if auhtor_str:
            authors.append(auhtor_str)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//section[@class='sky-form'][1]/p[@class='m_2'][3]/span/text()[1]").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str.replace("|", ""))
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
            "//span[contains(@style,'text-align')]/node()|//p[@align='center']/img")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p"]:
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
        read_count_str = response.xpath("//section[@class='sky-form'][1]/p[@class='m_2'][3]/span/text()[2]").get()
        if read_count_str:
            read_count = int(read_count_str.replace("views", "").strip())
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
