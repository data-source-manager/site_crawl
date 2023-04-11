# -*- coding: utf-8 -*-
import json
import re
import time
from urllib.parse import urljoin

from scrapy import Selector

from site_crawl.spiders.parser.base_parser import BaseParser

"""
    站点解析模版
"""


class CnHuanqiuParser(BaseParser):
    name = 'huanqiu'
    
    # 站点id
    site_id = "f438eb8f-e3ea-4927-92d2-7768d6798b8c"
    # 站点名
    site_name = "环球网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f438eb8f-e3ea-4927-92d2-7768d6798b8c", "source_name": "环球网", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("13708675-59e6-4fa9-ae8a-85f7a88dfb00", "军事", "https://mil.huanqiu.com/api/list?node=%22/e3pmh1dm8/e3pmt7hva%22,%22/e3pmh1dm8/e3pmtdr2r%22,%22/e3pmh1dm8/e3pn62l96%22,%22/e3pmh1dm8/e3pn6f3oh%22&offset=0&limit=20", "政治"),
            ("b335385f-501c-409a-8779-f76604a701c0", "台海", "https://taiwan.huanqiu.com/api/list?node=%22/e3pmh1fmg/e3pmh1g6o%22,%22/e3pmh1fmg/e3pmt8gfv%22,%22/e3pmh1fmg/e3pmt8i3n%22,%22/e3pmh1fmg/e3pmt8lic%22,%22/e3pmh1fmg/e3pmunk13%22,%22/e3pmh1fmg/e3pn6elbj%22&offset=0&limit=20", "政治"),
            ("dd707855-f9de-4c0a-a6d2-63ae041ebed7", "国内", "https://china.huanqiu.com/api/list?node=%22/e3pmh1nnq/e3pmh1obd%22,%22/e3pmh1nnq/e3pn61c2g%22,%22/e3pmh1nnq/e3pn6eiep%22,%22/e3pmh1nnq/e3pra70uk%22,%22/e3pmh1nnq/e5anm31jb%22,%22/e3pmh1nnq/e7tl4e309%22&offset=0&limit=20", "政治"),
            ("f2c569df-4beb-402d-95e5-01fc3fec2287", "国际", "https://world.huanqiu.com/api/list?node=%22/e3pmh22ph/e3pmh2398%22,%22/e3pmh22ph/e3pmh26vv%22,%22/e3pmh22ph/e3pn6efsl%22,%22/e3pmh22ph/efp8fqe21%22&offset=0&limit=20", "政治"),
            ("bff6c03b-6232-4830-9ac0-ed4ba63f540f", "评论", "https://opinion.huanqiu.com/api/list?node=%22/e3pmub6h5/e3pmub75a%22,%22/e3pmub6h5/e3pn00if8%22,%22/e3pmub6h5/e3pn03vit%22,%22/e3pmub6h5/e3pn4bi4t%22,%22/e3pmub6h5/e3pr9baf6%22,%22/e3pmub6h5/e3prafm0g%22,%22/e3pmub6h5/e3prcgifj%22,%22/e3pmub6h5/e81curi71%22,%22/e3pmub6h5/e81cv14rf%22,%22/e3pmub6h5/e81cv14rf/e81cv52ha%22,%22/e3pmub6h5/e81cv14rf/e81cv7hp0%22,%22/e3pmub6h5/e81cv14rf/e81cvaa3q%22,%22/e3pmub6h5/e81cv14rf/e81cvcd7e%22&offset=0&limit=20", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.article_dic = {}

    def parse_list(self, response) -> list:
        news_urls = json.loads(response.text).get("list")
        if news_urls:
            for news_url in news_urls:
                if news_url:
                    url_aid = news_url["aid"]
                    url = urljoin(response.url, url_aid).replace("api", "article")
                    self.article_dic[url] = {
                        "title": news_url["title"],
                        "pub": news_url["xtime"]
                    }
                    yield url

    def get_title(self, response) -> str:
        return self.article_dic[response.url].get("title").strip()

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//textarea[@class="article-author"]/text()').extract()
        if authors:
            for au in authors:
                if "：" in au:
                    au = au.split("：")[1]

                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = self.article_dic[response.url].get("pub").strip()
        if time_:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_) / 1000)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        content_html = re.findall('data-type="rtext">([\S\s]+)</section>', response.text)
        if content_html:
            news_tags = Selector(text=content_html[0]).xpath('//p|//video')
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "video":
                    con_media = self.parse_media(response, news_tag, media_type="mp4")
                    if con_media:
                        content.append(con_media)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        dic = {}
        if cons:
            if new_cons:
                dic['data'] = "".join(cons).strip()
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
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            if img.startswith("data:image/gif;base64"):
                return {}
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
