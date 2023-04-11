# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class SG_asiaoneParser(BaseParser):
    name = 'sg_asiaone'
    
    # 站点id
    site_id = "89a56833-2942-4ccd-bc3f-f402d9de0571"
    # 站点名
    site_name = "AsiaOne"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "89a56833-2942-4ccd-bc3f-f402d9de0571", "source_name": "AsiaOne", "direction": "sg", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("04fde21f-0089-3ceb-98d6-1746b22aba7b", "消息", "", "政治"),
            ("91235362-2f72-11ed-a768-d4619d029786", "消息/世界", "https://www.asiaone.com/world", "政治"),
            ("912352d6-2f72-11ed-a768-d4619d029786", "消息/中国", "https://www.asiaone.com/china", "政治"),
            ("912353ee-2f72-11ed-a768-d4619d029786", "消息/亚洲", "https://www.asiaone.com/asia", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        # news_urls = response.xpath("//ul[@class='ant-list-items']//li[@class='ant-list-item']/a/@href").extract() or []
        # if news_urls:
        #     for news_url in list(set(news_urls)):
        #         if not news_url.startswith('http'):
        #             news_url = urljoin(response.url, news_url)
        #         yield news_url
        yield "https://www.asiaone.com/world/thousands-russians-bid-farewell-last-soviet-leader-mikhail-gorbachev"

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='article-content']/h1[@class='title']/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        author_str = response.xpath("//span[@class='name-source']/a/text()").get()
        if author_str:
            author_list.append(author_str.strip())
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = response.xpath("//meta[@property='article:published_time']/@content").get()
        if datePublished_str:
            dt_ = datetime_helper.fuzzy_parse_timestamp(datePublished_str)
            dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt_))
            return str(dt)
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        tags_node = response.xpath("//meta[@property='article:tag']/@content").get()
        if tags_node:
            for tag in tags_node.split(","):
                tags_list.append(tag)
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='body']/*|"
                                   "//div[@class='image']/img|"
                                   "//div[@class='body']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
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

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip() and ".css-" not in x:
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@src').extract_first()

        if img and ".html" not in img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(
                       "./self::img/following-sibling::div/div[@class='image-caption']/text()|./following-sibling::figcaption/text()").extract_first(),
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath(".//@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.attrib.get('title'),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("").extract_first()
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
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
        comment_count = 0
        return comment_count

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
        repost_source_str = response.xpath("//a[@route='Source']/text()").get()
        print(repost_source_str)
        if repost_source_str:
            self.Dict[response.url] = {"repost": True}
            repost_source = repost_source_str
        return repost_source
