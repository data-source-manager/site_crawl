# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class HudsonParser(BaseParser):
    name = 'hudson'
    
    # 站点id
    site_id = "4ee38fba-0a52-42c3-8308-d3adc08f1f47"
    # 站点名
    site_name = "哈德逊研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "4ee38fba-0a52-42c3-8308-d3adc08f1f47", "source_name": "哈德逊研究所", "direction": "USA", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("b0f99bfe-e2ec-3e5e-8d63-4b784a263648", "主题", "", "政治"),
            ("40cad42d-bd5e-3729-ad57-f3822f0d3ca3", "主题/国家安全与国防", "https://www.hudson.org/national-security-defense", "政治"),
            ("fb604dc7-1ef2-3891-bf7d-66a0964e6928", "主题/对外政策", "https://www.hudson.org/foreign-policy", "政治"),
            ("8563276e-64f2-3f07-b513-264f56c6e26c", "主题/经济学", "https://www.hudson.org/economics", "政治"),
            ("688edc4f-ac46-327a-a986-76229a0d72ca", "地区", "", "政治"),
            ("8ff25922-4f2d-3365-8a34-0287f60a86f9", "地区/欧洲和中亚", "https://www.hudson.org/europe", "政治"),
            ("af810d25-30ec-317a-a563-536ddd5b0c8f", "政策中心", "", "政治"),
            ("1b6a0c8e-7bf2-369a-ad2c-0f2a0456d2a2", "政策中心/中国中心", "https://www.hudson.org/china-center", "政治"),
            ("4a8bcaee-fe6f-11ec-a30b-d4619d029786", "评论", "https://www.hudson.org/research/commentary", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "4ee38fba-0a52-42c3-8308-d3adc08f1f47"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h3/a/@href|//div[@class="research-card__title"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//header/h1/text()|//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="author"]/@content|'
                                 '//div[@id="block-mainpagecontent"]//div[@class="expert-author--names"]/a/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//div[@class="publication-meta"]/time[@class="date"]/@datetime|'
                               '//div[@class="hero__content"]//time/@datetime').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@class="topics-meta"]/ul/li/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath(
            '//figure[@class="figure lead"]|//div[contains(@class,"card__image")]/div[@class="field field-ed-header-image"]//img|'
            '//div[@id="block-mainpagecontent"]//div[contains(@class,"hero__image")]//img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//div[@class="field body"]/*|//div[@class="field body"]//iframe|'
                                   '//div[@class="field body"]/p/span/a|//div[@class="embedded_video"]/iframe')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "em"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "iframe":
                    con_file = self.parse_media(response, news_tag, media_type="mp3")
                    if con_file:
                        content.append(con_file)
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)
                if news_tag.root.tag == "figure":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

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
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip().replace('\xa0', '')
            if oneCons:
                if "Read in " in oneCons:
                    return []
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//figcaption//text()').extract()).strip(),
                   "src": img_url
                   }
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

    def parse_media(self, response, news_tag, media_type):
        videoUrl = news_tag.xpath("./@src").extract_first()

        video_dic = {}

        if videoUrl:
            if "youtube" in videoUrl:
                media_type = "mp4"
            suffix = f".{media_type}"

            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
            }

            if suffix == ".mp3":
                video_dic["type"] = "audio"
            elif suffix == ".mp4":
                video_dic["type"] = "video"

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
