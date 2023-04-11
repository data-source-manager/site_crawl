# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class JP_cnncoSiteParser(BaseParser):
    name = 'jp_cnnco'
    
    # 站点id
    site_id = "6d09c4e4-24c0-4104-bfb4-a5709387904a"
    # 站点名
    site_name = "有线电视新闻网日本网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "6d09c4e4-24c0-4104-bfb4-a5709387904a", "source_name": "有线电视新闻网日本网", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("076cb6f8-1f33-4daa-b238-7491c4994813", "专题", "", "政治"),
            ("1324bec7-24be-43b9-9f7b-45f78b956c88", "专题/乌克兰局势", "https://www.cnn.co.jp/topic/ukraine/", "政治"),
            ("d949fd6c-0efd-4f7f-8a22-a8f6abd7c888", "专题/斯里兰卡局势", "https://www.cnn.co.jp/topic/sri-lanka/", "政治"),
            ("72516524-ccb0-4538-963b-044571dee6b6", "专题/美国中期选举", "https://www.cnn.co.jp/topic/midterm-elections2022/", "政治"),
            ("81124cf6-faf7-4263-b1f4-c62b0c526777", "专题/联邦国会大厦突袭案", "https://www.cnn.co.jp/topic/capitol-riot/", "政治"),
            ("49f81c48-6feb-4fdc-9654-de7e52fb9af2", "世界", "https://www.cnn.co.jp/world/", "政治"),
            ("34bd07a8-f085-4a4b-84a9-d1a20b6757aa", "科技", "https://www.cnn.co.jp/tech/", "政治"),
            ("2276ceef-8728-451f-9067-5bf520e45b29", "美国", "https://www.cnn.co.jp/usa/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//section[3]//ul[@class='list-news-line']/li/a[1]/@href|"
                                   "//dl[@class='list-timeline']/dd/a[1]/@href").extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='ttl-headline-top']/text()|"
                               "//h1[@class='style-ttl']/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath("//div[@class='metadata-updatetime']/text()").extract_first()
        dt = time_.replace("posted at ", "")
        if dt:
            return str(datetime_helper.fuzzy_parse_datetime(dt))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath("//ul[@class='story-tag']/li/a/text()").extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath("//div[@id='leaf-body']/*|//div[@class='story-media-main']//img|"
                                   "//div[@id='leaf-body']//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "article"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "img":
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

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.attrib.get('alt'),
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
