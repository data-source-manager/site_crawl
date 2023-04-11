# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img

"""
    站点解析模版
"""


class UsaPotomacInstituteParser(BaseParser):
    name = 'usa_potomacinstitute'
    
    # 站点id
    site_id = "b2aaa7f7-0f29-4743-86bc-1b91813cb194"
    # 站点名
    site_name = "波托马克政策研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "b2aaa7f7-0f29-4743-86bc-1b91813cb194", "source_name": "波托马克政策研究所", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("866d790e-a919-11ed-95bd-1094bbebe6dc", "事件", "", "政治"),
            ("c1729631-fd96-3e96-8e25-cb722049088d", "事件/过去的事件", "https://www.potomacinstitute.org/events/past-events", "政治"),
            ("f3c00204-a911-11ed-9666-1094bbebe6dc", "刊物", "", "政治"),
            ("61a1c8ff-fa15-4ad4-a57b-3bfda1b81dd5", "刊物/报告", "https://potomacinstitute.org/publications/reports", "政治"),
            ("4aa46432-8b5d-4f54-b785-b9102d7d745c", "学术中心", "https://www.potomacinstitute.org/academic-centers", "政治"),
            ("d52aaaaf-7e5d-3df9-8604-edb448d83096", "学术中心/全球竞争项目（GCP）", "https://www.potomacinstitute.org/academic-centers/gcp", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="overlay-details"]/a/@href|//h4/a/@href|'
                                   '//h2[@itemprop="name"]/a/@href|//iframe/@src').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "youtube" in response.url:
            title = response.url
        else:
            title = response.xpath('//h2[@itemprop="headline"]/text()|//div[@class="page-title"]/h2/text()|'
                                   '//div[@class="ytp-title-text"]/a/text()').extract_first(
                default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@name="pubdate"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        if "youtube" in response.url:
            video_dic = {
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".mp4"
            }
            content.append(video_dic)
        news_tags = response.xpath('//p/a/img|//div[@itemprop="articleBody"]/p|//div[@itemprop="articleBody"]/p/a|'
                                   '//div[@itemprop="articleBody"]/div/span|//div[@itemprop="articleBody"]/div|'
                                   '//div[@itemprop="articleBody"]//div[@class="column"]/*|'
                                   '//div[@itemprop="articleBody"]/div/p|//div[contains(@class,"custom_html")]/*|'
                                   '//div[contains(@class,"custom_html")]//img|//li[@class="content-links-a"]/a|'
                                   '//iframe')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)
                if news_tag.root.tag == "iframe":
                    con_media = self.parse_media(response, news_tag, media_type="mp4")
                    if con_media:
                        content.append(con_media)

                if news_tag.root.tag == "img":
                    con_img = self.parse_single_img(response, news_tag)
                    if con_img:
                        content.extend(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""

        new_cons = []

        if cons:
            for con in cons:
                if con.strip():
                    new_cons.append({'data': "".join(con).strip(), 'type': "text"})
        return new_cons

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
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

    def parse_single_img(self, response, news_tag):
        img_list = []

        img_src = news_tag.xpath("./@src").extract_first()
        if check_img(img_src):
            img_url = urljoin(response.url, img_src)
            des = "".join(news_tag.xpath('.//figcaption//text()').extract()).strip()
            if not des:
                des = "".join(news_tag.xpath(".//img/@alt").extract())

            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', ""),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": des.strip(),
                   "src": img_url
                   }
            img_list.append(dic)
        return img_list

    def parse_many_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        imgs = news_tag.xpath('.//img')

        img_list = []

        if imgs:
            for img in imgs:
                img_src = img.xpath("./@src").extract_first()
                if check_img(img_src):
                    img_url = urljoin(response.url, img_src)
                    des = "".join(news_tag.xpath('.//figcaption//text()').extract()).strip()
                    if not des:
                        des = "".join(img.xpath(".//img/@alt").extract())

                    dic = {"type": "image",
                           "name": img.attrib.get('title', ""),
                           "md5src": self.get_md5_value(img_url) + '.jpg',
                           "description": des.strip(),
                           "src": img_url
                           }
                    img_list.append(dic)

        return img_list

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
        suffix = f".{media_type}"

        video_dic = {}

        if videoUrl:
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
