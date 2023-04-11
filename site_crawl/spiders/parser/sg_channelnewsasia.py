# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from util.tools import check_img
from .base_parser import BaseParser


class SgChannelnewsasiaParser(BaseParser):
    name = 'sg_channelnewsasia'
    
    # 站点id
    site_id = "e34c46b4-faea-4768-a7bb-062106457029"
    # 站点名
    site_name = "亚洲新闻网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e34c46b4-faea-4768-a7bb-062106457029", "source_name": "亚洲新闻网", "direction": "sg", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d257e-fe6f-11ec-a30b-d4619d029786", "世界", "https://www.channelnewsasia.com/world", "政治"),
            ("4a8d24ca-fe6f-11ec-a30b-d4619d029786", "亚洲", "https://www.channelnewsasia.com/asia", "政治"),
            ("4a8d25d8-fe6f-11ec-a30b-d4619d029786", "商业", "https://www.channelnewsasia.com/business", "政治"),
            ("4a8d2524-fe6f-11ec-a30b-d4619d029786", "新加坡", "https://www.channelnewsasia.com/singapore", "政治"),
            ("55974513-7613-4c6f-acd7-dafe6e99f732", "最新消息", "https://www.channelnewsasia.com/latest-news", "政治"),
            ("4a8d2466-fe6f-11ec-a30b-d4619d029786", "评论", "https://www.channelnewsasia.com/commentary", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h5[@class="h5 list-object__heading"]/a/@href|'
                                   '//h6[@class="h6 list-object__heading"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                url = urljoin(response.url, news_url)
                if "watch" in url or "listen" in url or "interactives" in url:
                    continue
                if "www.channelnewsasia.com" in url:
                    yield url

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@name="cXenseParse:recs:publishtime"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//meta[@name="keywords"]/@content').extract_first()
        if tags:
            if "," in tags:
                tags = tags.split(",")
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//article/div[@class="content"]//div[contains(@class,"layout__region--first")]/section//img|'
            '//article/div[@class="content"]//div[contains(@class,"layout__region--first")]/section//div[@class="text-long"]/*|'
            '//div[contains(@class,"content-detail__description")]/text()|'
            '//div[contains(@class,"content-detail__description")]|*'
            '//article/div[@class="content"]//div[contains(@class,"region--content")]/section//div[@class="text-long"]/*|'
            '//article/div[@class="content"]//div[contains(@class,"region--content")]/section//img|'
            '//div[@class="podcast-main__description"]/*')
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
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
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
                des = "".join(news_tag.xpath(".//@alt").extract())

            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', ""),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": des.strip(),
                   "src": img_url
                   }
            img_list.append(dic)
        return img_list

    def parse_many_img(self, response, news_tag):
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
                           "name": img.attrib.get('title', None),
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
        read_count = 0
        read_count_str = response.xpath("//span[contains(@class,'views post-meta-views')]/text()").get()
        if read_count_str:
            read_count = int(read_count_str.replace(",", ""))
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
