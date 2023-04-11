# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class BR_folhauolParser(BaseParser):
    name = 'br_folhauol'
    
    # 站点id
    site_id = "4b87f08e-67f5-4465-9870-7bfe1b96b00c"
    # 站点名
    site_name = "圣保罗页报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "4b87f08e-67f5-4465-9870-7bfe1b96b00c", "source_name": "圣保罗页报", "direction": "br", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91235b50-2f72-11ed-a768-d4619d029786", "世界", "https://www1.folha.uol.com.br/mundo/", "政治"),
            ("91235aec-2f72-11ed-a768-d4619d029786", "政策", "https://www1.folha.uol.com.br/poder/#10", "政治"),
            ("91235b1e-2f72-11ed-a768-d4619d029786", "经济", "https://www1.folha.uol.com.br/mercado/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//li[@class='c-headline c-headline--newslist']//div[@class='c-headline__content']/a")
        if news_urls:
            for news_url in news_urls:
                rsp_url = news_url.xpath('./@href').get()
                rsp_title = news_url.xpath('./h2/text()').get()
                self.Dict[rsp_url] = {'title': rsp_title}
                if "/2922/" not in rsp_url:
                    yield rsp_url

    def get_title(self, response) -> str:
        title = self.Dict[response.url]['title']
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        author_strs = response.xpath("//strong[@class='c-signature__author']/a/text()").getall()
        if author_strs:
            author_list.extend(author_strs)
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
        tags_node = response.xpath("//ul[@class='c-topics__list']/li[@class='c-topics__item']/a/text()").getall()
        if tags_node:
            tags_list.extend(tags_node)

        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@itemprop='articleBody']/*|//div[@itemprop='articleBody']//img")
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
                        content.extend(text_dict)

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
        img = news_tag.xpath('./@data-src|./@src').extract_first()

        if img and ".html" not in img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath("./@alt").extract_first(),
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
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
