# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class HK_takungpaoParser(BaseParser):
    name = 'hk_takungpao'
    
    # 站点id
    site_id = "9fe95503-0d12-4729-be0b-3abbee6417f5"
    # 站点名
    site_name = "大公网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "9fe95503-0d12-4729-be0b-3abbee6417f5", "source_name": "大公网", "direction": "hk", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("05e1774d-218c-30dd-ba3a-eb95f38eb4c7", "新闻", "", "政治"),
            ("4a8de842-fe6f-11ec-a30b-d4619d029786", "新闻/两岸", "http://www.takungpao.com/news/232110/index.html", "政治"),
            ("4a8deb44-fe6f-11ec-a30b-d4619d029786", "新闻/内地", "http://www.takungpao.com/news/232108/index.html", "政治"),
            ("4a8de900-fe6f-11ec-a30b-d4619d029786", "新闻/军事", "http://www.takungpao.com/news/232112/index.html", "政治"),
            ("4a8de9aa-fe6f-11ec-a30b-d4619d029786", "新闻/国际", "http://www.takungpao.com/news/232111/index.html", "政治"),
            ("4a8dec7a-fe6f-11ec-a30b-d4619d029786", "新闻/大公访谈", "http://www.takungpao.com/news/232113/index.html", "社会"),
            ("4a8dea4a-fe6f-11ec-a30b-d4619d029786", "新闻/港闻", "http://www.takungpao.com/news/232109/index.html", "政治"),
            ("b0c22106-7218-11ed-a54c-d4619d029786", "港闻", "http://www.takungpao.com/news/232109/index.html", "政治"),
            ("9ae58089-aa53-3d0e-bc7d-f9d798f209ec", "评论", "http://www.takungpao.com/opinion/index.html", "政治"),
            ("4a8def86-fe6f-11ec-a30b-d4619d029786", "评论/公平世界", "http://www.takungpao.com/opinion/233123/index.html", "政治"),
            ("4a8df01c-fe6f-11ec-a30b-d4619d029786", "评论/大公评论", "http://www.takungpao.com/opinion/233119/index.html", "政治"),
            ("4a8deef0-fe6f-11ec-a30b-d4619d029786", "评论/点击香江", "http://www.takungpao.com/opinion/233161/index.html", "政治"),
            ("4a8dee5a-fe6f-11ec-a30b-d4619d029786", "评论/纵横谈", "http://www.takungpao.com/opinion/233117/index.html", "政治"),
            ("4a8ded9c-fe6f-11ec-a30b-d4619d029786", "评论/隔海观澜", "http://www.takungpao.com/opinion/233116/index.html", "政治"),
            ("c687dc6e-a068-11ed-a64d-1094bbebe6dc", "财经", "", "政治"),
            ("e8f945dc-d0f0-4b7c-9769-986e825e2b10", "财经/商业", "http://www.takungpao.com/news/232109/index.html", "政治"),
            ("854c324e-581f-3602-bc0b-7c3385279796", "财经/经济观察家", "http://www.takungpao.com/finance/236134/index.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "9fe95503-0d12-4729-be0b-3abbee6417f5"
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//dl[@class='item clearfix']/dd[1]/a/@href|//dl[@class='item']/dd[@class='title']/a/@href|"
            "//div[@class='wrap_left']/dl/dd[@class='intro']/a/@href").extract() or []
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h2[@class='tkp_con_title']/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_a = response.xpath("//div[@class='tkp_con_author']/text()[normalize-space()]").get()
        if author_a:
            authors.append(author_a.replace("作者：", "").strip())
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//div[@class='tkp_con_author']/span[1]/text()").get()

        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags = response.xpath("//div[@class='jeg_inner_content']/div[@class='jeg_post_tags']/a/text()").getall()
        if tags:
            tags_list.extend(tags)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='tkp_content']/*|//div[@class='video_wrap']//video|"
                                   "//div[@class='tkp_content']")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", 'center', "div"]:
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
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        if self.Dict.get(response.url):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        repost_source_str = response.xpath("//div[@class='tkp_con_author']/span[2]/text()").get()
        if repost_source_str:
            self.Dict[response.url] = repost_source_str
            repost_source = repost_source_str
        return repost_source
