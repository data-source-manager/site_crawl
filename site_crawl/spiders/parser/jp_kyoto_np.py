# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class JpkyotoParser(BaseParser):
    name = 'kyoto'

    # 站点id
    site_id = "fe46f840-c50e-4787-9f2b-204c210afa87"
    # 站点名
    site_name = "京都新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "fe46f840-c50e-4787-9f2b-204c210afa87", "source_name": "京都新闻", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块主题)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("09798a1e-f7ee-491b-81b9-da9f653a499a", "国内", "https://www.kyoto-np.co.jp/category/news-kyodo", "政治"),
            ("cda7920d-9538-4526-8cb0-c0291f88aa37", "京都", "", "政治"),
            ("6939e2b3-8ff2-4e62-b2f5-9550d3dff71f", "京都/京都市", "https://www.kyoto-np.co.jp/category/news-kyodo", "政治"),
            ("2f064f40-070f-4b6c-a422-238a03283fd8", "京都/山城", "https://www.kyoto-np.co.jp/category/news-kyodo", "政治"),
            ("03f93563-1148-48d9-b709-bc8251a982c3", "京都/洛西", "https://www.kyoto-np.co.jp/category/news-kyodo", "政治"),
            ("ebf6637c-9c15-45ad-b3f0-d36e0f4484b8", "京都/丹波", "https://www.kyoto-np.co.jp/category/news-kyodo", "政治"),
            ("1fdbf800-93c2-4b11-a80d-5068a8a9d691", "京都/中丹", "https://www.kyoto-np.co.jp/category/news-kyodo", "政治"),
            ("4f70d84a-dbe2-4992-94bd-6dbe3872f909", "京都/探戈", "https://www.kyoto-np.co.jp/category/news-kyodo", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//article[@class="m-articles-item"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        2023-03-07 11:35
        """
        time_ = response.xpath('//time/@datetime').extract_first()
        if time_:
            pub_time = datetime.strptime(time_, "%Y-%m-%d %H:%M")
            return datetime_helper.parseTimeWithOutTimeZone(pub_time, site_name="京都新闻")

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[contains(@class,"article-body")]/p|//div[contains(@class,"article-body")]//div[@class="slide"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag == "div":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", ]:
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
        cons = news_tag.xpath("./text()").extract() or ""
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
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(".//p/text()").extract_first(),
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
