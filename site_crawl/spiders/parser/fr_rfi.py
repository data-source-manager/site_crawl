# -*- coding: utf-8 -*-
# update:(liyun|2023-01-31) -> 板块核对与解析代码修正
import json
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class FrRfiParser(BaseParser):
    name = 'rfi'
    
    # 站点id
    site_id = "8fa19fa5-cbf3-458b-ae5a-b6bc936ae52d"
    # 站点名
    site_name = "法国国际广播电台"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "8fa19fa5-cbf3-458b-ae5a-b6bc936ae52d", "source_name": "法国国际广播电台", "direction": "fr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b3ec6-fe6f-11ec-a30b-d4619d029786", "乌克兰", "https://www.rfi.fr/fr/tag/ukraine/", "政治"),
            ("6ff4504e-1ca0-41e0-9670-3a28c60e9730", "地区", "", "政治"),
            ("9576493d-d9c3-42ad-b07e-7e1957563ad4", "地区/中东", "https://www.rfi.fr/fr/moyen-orient/", "政治"),
            ("d5b16295-2a94-4e30-951d-1976713b4f0e", "地区/亚太地区", "https://www.rfi.fr/fr/asie-pacifique/", "政治"),
            ("1543a46d-a49e-4d3b-a953-e34b87736db0", "地区/国际的", "https://www.rfi.fr/fr/monde/", "政治"),
            ("63d2ef0f-6707-40c6-b63b-967d2793a482", "地区/欧洲", "https://www.rfi.fr/fr/europe/", "政治"),
            ("1da68150-83ba-44cc-982e-08065a1681e2", "地区/法国", "https://www.rfi.fr/fr/france/", "政治"),
            ("0a898a7b-ffde-40ec-ab40-644928cd7e79", "地区/美洲", "https://www.rfi.fr/fr/am%C3%A9riques/", "政治"),
            ("52b146e9-dda9-4fd8-904f-89a159427421", "地区/非洲", "https://www.rfi.fr/fr/afrique/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "8fa19fa5-cbf3-458b-ae5a-b6bc936ae52d"

    def parse_list(self, response) -> list:
        # news_urls = response.xpath('//div[contains(@class,"m-item-list-article")]/a/@href').extract() or []
        news_urls = [
            urljoin(response.url, url)
            for url in response.xpath('//a[@data-article-item-link]/@href').extract() or []
        ]
        filter = {
            "https://www.rfi.fr/ff/",
            "https://www.rfi.fr/ha/",
            "https://www.rfi.fr/ma/",
            "https://www.rfi.fr/sw/",
            "https://www.rfi.fr/en/africa/",
            "https://www.rfi.fr/pt/%C3%A1frica/",

        }
        for news_url in list(set(news_urls) - filter):
            yield news_url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        authors = response.xpath('//a[@class="m-from-author__name"]/@title').extract()
        return [a.strip() for a in authors]

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags = response.xpath('//ul[@class="m-tags-list"]/li/a/text()').extract()
        return [t.strip() for t in tags]

    def get_content_media(self, response) -> list:
        content = []
        # 解析媒体数据
        try:
            video = json.loads(response.xpath('//script[@data-media-video-id]/text()').extract_first())
            video_url = video["sources"][0]["url"]
            content.append({
                "type": "video",
                "src": video_url,
                "name": video["mediaId"],
                "description": None,
                "md5src": self.get_md5_value(video_url) + ".mp4"
            })
        except:
            pass
        try:
            audio = json.loads(response.xpath('//button[@class="m-feed-sub__audio"]/script/text()').extract_first())
            audio_url = audio["sources"][0]["url"]
            content.append({
                "type": "audio",
                "src": audio_url,
                "name": audio["mediaId"],
                "description": None,
                "md5src": self.get_md5_value(audio_url) + ".mp3"
            })
        except:
            pass
        # 解析正文数据
        news_tags = response.xpath("//article/div[contains(@class,'content__body')]/*|"
                                   "//article/div[contains(@class,'main-media')]/figure")
        if news_tags:
            for tag in news_tags:
                # 解析文本数据
                if tag.root.tag in ["p", "h2", "h4"]:
                    con_text = self.parse_text(tag)
                    if con_text:
                        content.extend(con_text)
                if tag.root.tag in ["ul", "ol"]:
                    con_text = self.parse_text(tag)
                    if con_text:
                        content.extend(con_text)
                # 解析图像数据
                elif tag.root.tag == "figure":
                    con_img = self.parse_img(response, tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "fr"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if not x.startswith("Newsletter") and x.strip():
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
                dic['data'] = oneCons.replace("\t\n", "")
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@srcset').extract_first()
        if img:
            if "," in img:
                img = img.split(",")[0].split(" ")[0].strip()
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath("./figcaption//text()").extract()).strip(),
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
