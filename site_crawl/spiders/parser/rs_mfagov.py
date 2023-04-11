# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class RS_mfagovParser(BaseParser):
    name = 'rs_mfagov'
    
    # 站点id
    site_id = "462434f1-6e12-459b-8793-a7f9d5b9a839"
    # 站点名
    site_name = "塞尔维亚外交部"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "462434f1-6e12-459b-8793-a7f9d5b9a839", "source_name": "塞尔维亚外交部", "direction": "rs", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("41160cde-80d9-3ffc-9963-2fc99f183a3d", "新闻服务", "", "政治"),
            ("91236654-2f72-11ed-a768-d4619d029786", "新闻服务/声明", "https://www.mfa.gov.rs/en/press-service/statements", "政治"),
            ("912365d2-2f72-11ed-a768-d4619d029786", "新闻服务/消息", "https://www.mfa.gov.rs/en/press-service/news", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//a[@class='link link--absolute']/@href").extract() or []
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='field field--title']/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = response.xpath("//div[@class='field field--date']/text()").get()
        if datePublished_str:
            Date_mt = datetime_helper.fuzzy_parse_datetime(datePublished_str)
            return str(Date_mt)
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath(
            "//div[@class='field field--intro']|//div[@class='field field--text']/*|//div[@class='field field--gallery']//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h1", "h2", "h3", "h4", "h5", "p"] or news_tag.root.get("class",
                                                                                                 "") == 'field field--intro':
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "div" and "media" in news_tag.root.get("class", ""):
                    con_video = self.parse_media(response, news_tag)
                    if con_video:
                        content.append(con_video)
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
        """"
            可以对一个标签下存在多个段落进行解析
        """
        dic = {}
        cons = news_tag.xpath(".//text()").extract() or ""
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

    def parse_img(self, response, news_tag, img_xpath='', img_des=''):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath(img_xpath).extract_first()

        if img and ".html" not in img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": None,
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
        videoUrl = news_tag.xpath(".//iframe/@src").extract_first()
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
        repost_source_str = response.xpath("//*[text()[contains(.,'Source:')]]/text()").get()
        if repost_source_str:
            repost_source = repost_source_str.replace("Source:", "").strip()
            self.Dict[response.url] = repost_source
        return repost_source
