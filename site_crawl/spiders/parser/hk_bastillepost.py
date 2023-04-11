# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.site_deal import interface_helper
# from util.site_deal import interface_helper
from .base_parser import BaseParser


class HK_bastillepostParser(BaseParser):
    name = 'hk_bastillepost'
    
    # 站点id
    site_id = "b3b82fde-a4f5-4789-b216-07e1173ea33b"
    # 站点名
    site_name = "巴士滴报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "b3b82fde-a4f5-4789-b216-07e1173ea33b", "source_name": "巴士滴报", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("a761edb3-2a55-4a57-96dd-bca14ad7bd39", "两岸", "https://www.bastillepost.com/hongkong/category/127614-兩岸", "政治"),
            ("ca8a89f6-f3fe-39d3-c726-4c9dc060ab04", "其他", "", "政治"),
            ("916ee684-32ae-9502-3f1b-d29f66e5d115", "其他/香港电台", "", "政治"),
            ("7e3bf71a-4c19-468c-854a-cbfb81e2bb42", "其他/香港电台/国际新闻", "https://www.bastillepost.com/hongkong/category/177010-%E5%9C%8B%E9%9A%9B%E6%96%B0%E8%81%9E", "政治"),
            ("a207a6c3-d23b-41ac-9ee4-125c2e5dc70a", "其他/香港电台/大中华新闻", "https://www.bastillepost.com/hongkong/category/245310-%E5%A4%A7%E4%B8%AD%E8%8F%AF%E6%96%B0%E8%81%9E", "政治"),
            ("cf116fc3-0029-4385-a5f7-4d9649b8e1b1", "其他/香港电台/本地新闻", "https://www.bastillepost.com/hongkong/category/177009-%E6%9C%AC%E5%9C%B0%E6%96%B0%E8%81%9E", "政治"),
            ("86dacbcc-76c0-4ab1-bc86-adc736264609", "其他/香港电台/财经新闻", "https://www.bastillepost.com/hongkong/category/245311-%E8%B2%A1%E7%B6%93%E6%96%B0%E8%81%9E", "政治"),
            ("6619c3e3-f670-48ba-9502-6f660510a0a4", "内地抗疫快讯", "https://www.bastillepost.com/hongkong/category/200127-%E5%85%A7%E5%9C%B0%E6%8A%97%E7%96%AB%E5%BF%AB%E8%A8%8A", "政治"),
            ("4a8de7ca-fe6f-11ec-a30b-d4619d029786", "大视野", "https://www.bastillepost.com/hongkong/category/6-%E5%A4%A7%E8%A6%96%E9%87%8E", "政治"),
            ("4a8de766-fe6f-11ec-a30b-d4619d029786", "政事", "https://www.bastillepost.com/hongkong/category/1-政事", "政治"),
            ("aabb0a44-8f70-4617-8419-a70c41fd7496", "权威数据库", "https://www.bastillepost.com/hongkong/category/206030-國安法資料庫", "政治"),
            ("5990fbdc-24c6-4a2b-8153-3f526e66e47c", "社会事", "https://www.bastillepost.com/hongkong/category/3-%E7%A4%BE%E6%9C%83%E4%BA%8B", "政治"),
            ("86705441-b5d9-4d9a-834e-cd810442b908", "立议选站", "https://www.bastillepost.com/hongkong/category/233094-%E7%AB%8B%E6%9C%83%E9%81%B8%E6%88%B0", "政治"),
            ("fd3c68db-9b90-4924-a16d-f3cc96cda3aa", "钱财事", "https://www.bastillepost.com/hongkong/category/5-%E9%8C%A2%E8%B2%A1%E4%BA%8B", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "b3b82fde-a4f5-4789-b216-07e1173ea33b"
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//article[contains(@class,'article')]/div[2]/h3/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='cat-theme-color']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_a = response.xpath("//div[@class='tkp_con_author']/text()[normalize-space()]").get()
        if author_a:
            authors.append(author_a.replace("作者：", "").strip())
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//header[@class='article-heading']//time/@datetime").get()

        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//header[@class='article-heading']/img|//section[@class='single-article']/*|//section[@class='single-article']//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'center']:
                    if news_tag.xpath(".//img"):
                        img_src = self.parse_img(response, news_tag, img_xpath=".//img/@src", des_xpath=".//img/@alt")
                        if img_src:
                            content.append(img_src)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                elif news_tag.root.tag == 'img':
                    img_src = self.parse_img(response, news_tag, img_xpath="./@src", des_xpath="./@alt")
                    if img_src:
                        content.append(img_src)
                elif news_tag.root.tag == 'video':
                    video_src = self.parse_media(response, news_tag)
                    if video_src:
                        content.append(video_src)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip() and "往下看更多文章" not in x:
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url and "scorecardresearch" not in img_url:
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
        like_count_str = interface_helper.request_interface(
            "//*[text()[contains(.,'Like')]]/following-sibling::span/text()", response.url)

        return int(like_count_str) if like_count_str else 0

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
