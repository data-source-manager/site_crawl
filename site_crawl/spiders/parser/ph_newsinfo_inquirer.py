# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class PH_inquirerParser(BaseParser):
    name = 'ph_inquirer'
    
    # 站点id
    site_id = "394fbc0a-7601-4cda-a024-af40c1206344"
    # 站点名
    site_name = "菲律宾日报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "394fbc0a-7601-4cda-a024-af40c1206344", "source_name": "菲律宾日报", "direction": "ph", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("cd755e17-f04c-46ca-a1b5-eaffd5093d00", "消息", "", "政治"),
            ("ac9960b7-21b6-4737-9ad7-84b2e4c520cd", "消息/世界", "https://newsinfo.inquirer.net/category/world-latest-stories", "政治"),
            ("be6380e5-6db8-4ea9-ab36-2a7a8941e0b3", "观点", "https://opinion.inquirer.net/category/inquirer-opinion/letters-to-the-editor", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//div[@id='ch-ls-head']/h2/a/@href").extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='entry-title']/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished = response.xpath("//meta[@property='article:published_time']/@content").extract_first()
        if datePublished:
            dt = datetime_helper.fuzzy_parse_timestamp(datePublished)
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
        news_tags = response.xpath("//div[@id='article_content']/div/*|//div[@id='article_content']/div//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    if "TAGS: " in news_tag.xpath(".//text()").getall():
                        break
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        if "#article_content p.headertext" not in text_dict[0].get("data"):
                            content.extend(text_dict)

                if news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def parseOnetext(self, news_tag) -> list:
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip()
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

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

        if img and ".svg" not in img and "inqplus-left.png" not in img and "inqplus-right.png" not in img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(
                       './self::img/following-sibling::p[@class="wp-caption-text"]/text()').extract_first() or None,
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
