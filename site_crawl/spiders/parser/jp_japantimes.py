# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class JP_japantimesParser(BaseParser):
    name = 'jp_japantimes'
    
    # 站点id
    site_id = "895b06d1-5a2c-5077-e40b-6e82e37208c4"
    # 站点名
    site_name = "日本时报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "895b06d1-5a2c-5077-e40b-6e82e37208c4", "source_name": "日本时报", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("ca418e3b-99d8-3933-91b8-8503d0c2fcca", "消息", "", "政治"),
            ("912340ca-2f72-11ed-a768-d4619d029786", "消息/世界", "https://www.japantimes.co.jp/news/world/", "政治"),
            ("9123403e-2f72-11ed-a768-d4619d029786", "消息/亚太地区", "https://www.japantimes.co.jp/news/asia-pacific/", "政治"),
            ("91233fa8-2f72-11ed-a768-d4619d029786", "消息/国内的", "https://www.japantimes.co.jp/news/", "政治"),
            ("7349c900-3767-3c21-9d06-40d9ad35cae0", "观点", "", "政治"),
            ("91234156-2f72-11ed-a768-d4619d029786", "观点/社论", "https://www.japantimes.co.jp/opinion/editorials/", "政治"),
            ("912341e2-2f72-11ed-a768-d4619d029786", "观点/评论", "https://www.japantimes.co.jp/opinion/commentary/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//header//p/a/@href").extract() or ""
        if response.url == "https://www.japantimes.co.jp/news/":
            news_urls = response.xpath("//section[@class='module'][1]//hgroup/p/a/@href").extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='padding_block single-title']/h1/text()|"
                               "//div[@class='padding_block single-post-title']/h1/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath("//meta[@property='article:published_time']/@content").extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath("//div[@id='jtarticle']/*|//figure[@class='slide_image']//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "ja"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.attrib.get('alt'),
                   "src": urljoin(response.url, news_tag.attrib.get('src'))}
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
