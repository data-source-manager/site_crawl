# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img

"""
    模版
"""


class IdAntArAnewsParser(BaseParser):
    name = 'id_antaranews'
    
    # 站点id
    site_id = "df700beb-4fc7-4a59-8b47-80d3de48a6be"
    # 站点名
    site_name = "印度尼西亚安塔拉通讯社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "df700beb-4fc7-4a59-8b47-80d3de48a6be", "source_name": "印度尼西亚安塔拉通讯社", "direction": "id", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d797a-fe6f-11ec-a30b-d4619d029786", "世界", "", "政治"),
            ("505353b7-9458-4b3a-87b5-0e3480ff1abc", "世界/东盟", "https://www.antaranews.com/dunia/asean", "政治"),
            ("84d72c54-1bb5-409d-926a-fb4018ceac2c", "世界/国际", "https://www.antaranews.com/dunia/internasional", "政治"),
            ("436d682d-a918-416a-b073-58446780ef11", "世界/国际角", "https://www.antaranews.com/dunia/internasional-corner", "政治"),
            ("4a8d7916-fe6f-11ec-a30b-d4619d029786", "政治", "https://www.antaranews.com/politik", "政治"),
            ("4a8d7948-fe6f-11ec-a30b-d4619d029786", "法律", "https://www.antaranews.com/hukum", "政治"),
            ("4a2c1ab8-efd4-4c81-9b00-04b0ed4a9064", "经济", "", "政治"),
            ("ecc23f24-d4b7-44e4-981c-aa6cda9c3ed4", "经济/BUMN 印度尼西亚", "https://www.antaranews.com/ekonomi/bumn-untuk-indonesia", "政治"),
            ("fcbd3e13-c154-47be-a47a-9c57654b968b", "经济/交换", "https://www.antaranews.com/ekonomi/bursa", "政治"),
            ("49344b17-4bcb-4b28-8ec2-8f207f88258d", "经济/商业", "https://www.antaranews.com/ekonomi/bisnis", "政治"),
            ("4a1b35a8-6ab2-4d82-842d-e1d26598ab7a", "经济/金融", "https://www.antaranews.com/ekonomi/finansial", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//article[@class="simple-post simple-big clearfix"]/div/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="post-title"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//ul[@class="tags-widget clearfix"]//a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//header[@class="post-header clearfix"]/figure[@class="image-overlay"]//img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//div[@class="Ar Au Ao"]/*|'
                                   '//div[contains(@class,"post-content")]/text()|'
                                   '//div[contains(@class,"post-content")]/*|'
                                   '//video[@id="videoplayer"]/source[1]|'
                                   '//div[contains(@class,"margin-top-15")]/text()|'
                                   '//div[@class="flex-caption"]/*|'
                                   '//div[@class="single-image"]/img|'
                                   '//div[@id="thumb_list"]/div//img')
        img_set = set()
        img_set = set()
        if news_tags:
            for news_tag in news_tags:
                if type(news_tag.root) == str:
                    con = news_tag.root.strip()
                    if con:
                        content.append({
                            "type": "text",
                            "data": con
                        })
                else:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "b"]:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                    if news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            con_text = self.parseOnetext(con)
                            if con_text:
                                content.extend(con_text)
                    if news_tag.root.tag == "source":
                        con_media = self.parse_media(response, news_tag, media_type="video")
                        if con_media:
                            content.append(con_media)

                    if news_tag.root.tag == "img":
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            src = con_img.get("src")
                            if src not in img_set:
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
            oneCons = "".join(cons).strip()
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@data-src').extract_first()
        if check_img(img):
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
        if media_type == "video":
            suffix = ".mp4"
        else:
            suffix = ".mp3"
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
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
