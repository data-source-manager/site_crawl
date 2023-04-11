# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class FrFrance24Parser(BaseParser):
    name = 'france24'
    
    # 站点id
    site_id = "4de556f3-dcb4-4f2c-b3fe-ea5689c71d48"
    # 站点名
    site_name = "法兰西24"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "4de556f3-dcb4-4f2c-b3fe-ea5689c71d48", "source_name": "法兰西24", "direction": "fr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b6cca-fe6f-11ec-a30b-d4619d029786", "中国", "https://www.france24.com/en/tag/china/", "政治"),
            ("4a8b6c8e-fe6f-11ec-a30b-d4619d029786", "乌克兰战争", "https://www.france24.com/en/tag/ukraine/", "政治"),
            ("4a8b6cfc-fe6f-11ec-a30b-d4619d029786", "俄罗斯", "https://www.france24.com/en/tag/russia/", "政治"),
            ("4a8b6d2e-fe6f-11ec-a30b-d4619d029786", "台湾", "https://www.france24.com/en/tag/taiwan/", "政治"),
            ("c24a2c96-f6d3-6710-6c05-537ab24a9253", "新闻", "", "政治"),
            ("af37e173-8e92-4a0a-a112-36f88a16e2fe", "新闻/中东", "https://www.france24.com/en/middle-east/", "政治"),
            ("0ebd8ccb-5ad7-4877-9686-f11c6c7c851a", "新闻/亚太", "https://www.france24.com/en/asia-pacific/", "政治"),
            ("dcbc090b-c8fb-4048-bfd3-e526048c52a8", "新闻/欧洲", "https://www.france24.com/en/europe/", "政治"),
            ("f1d4127c-0b0e-4fc6-9109-d7f7dee05417", "新闻/法国", "https://www.france24.com/en/france/", "政治"),
            ("18207a67-2760-4645-bbfe-341b9387941e", "新闻/美洲", "https://www.france24.com/en/americas/", "政治"),
            ("d6261836-1ca8-4c22-ba7e-11a11cf9ab7c", "新闻/非洲", "https://www.france24.com/en/africa/", "政治"),
            ("4a8b6ebe-fe6f-11ec-a30b-d4619d029786", "欧洲联盟", "https://www.france24.com/en/tag/european-union/", "政治"),
            ("4a8b6e1e-fe6f-11ec-a30b-d4619d029786", "美国", "https://www.france24.com/en/tag/usa/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "4de556f3-dcb4-4f2c-b3fe-ea5689c71d48"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="o-layout-list "]/div//a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                url = urljoin(response.url, news_url)
                if "france24" in url:
                    yield url

    def get_title(self, response) -> str:
        title = response.xpath('//h1[contains(@class,"content__title")]/text()|'
                               '//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//div[@class="m-from-author"]/a[contains(@class,"author")]/text()').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//ul[@class="m-tags-list"]/li/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        video = response.xpath("//video-player")
        if video:
            video_link = self.parse_media(response, video)
            if video_link:
                content.append(video_link)
        else:
            img_list = response.xpath('//div[@class="t-content__main-media"]//img')
            if img_list:
                for img in img_list:
                    content.append(self.parse_img(response, img))

        news_tags = response.xpath('//div[contains(@class,"content__body")]/p|'
                                   '//article/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
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
                if x.strip():
                    dic['data'] = x.strip().replace('\xa0', '')
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
        img = news_tag.xpath('./@srcset').extract_first()
        if img:
            if "," in img:
                img = img.split(",")[0].split(" ")[0]
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.attrib.get('alt'),
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
        videoUrl = news_tag.xpath("./@source").extract_first()
        if videoUrl:
            # video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": videoUrl,
                "name": None,
                "description": news_tag.xpath("./@alt").extract_first(),
                "md5src": self.get_md5_value(videoUrl) + ".mp4"
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
