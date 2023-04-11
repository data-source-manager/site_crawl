# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class TW_twincnParser(BaseParser):
    name = 'tw_twincn'
    
    # 站点id
    site_id = "15f7fa7c-5505-11ed-b241-6030d461e866"
    # 站点名
    site_name = "网络温度计"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "15f7fa7c-5505-11ed-b241-6030d461e866", "source_name": "网络温度计", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9a640683-ef91-399b-8c7b-da6364650a91", "数据研究室", "", "政治"),
            ("a50db805-f033-3028-b05a-e34565ebde05", "数据研究室/政治", "https://dailyview.tw/InsightArticle?cateCode=politics", "政治"),
            ("4a00f9a3-e147-34d4-863b-4bf977b73dc5", "数据研究室/洞察报告", "https://dailyview.tw/InsightReport", "政治"),
            ("541a4abb-a50c-308e-a703-5cf02575a9c8", "民调中心", "https://dailyview.tw/specialreport/detail/4", "政治"),
            ("00ba228c-1888-3587-b695-a94d2d17ac84", "网络爆红新闻", "", "政治"),
            ("e510164b-4f54-3ddb-9cae-770e8b7a45a8", "网络爆红新闻/国际", "https://dailyview.tw/Popular?cate=international", "政治"),
            ("a50db805-f033-3028-b05a-e34565ebde05", "网络爆红新闻/政治", "https://dailyview.tw/Popular?cate=politics", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "15f7fa7c-5505-11ed-b241-6030d461e866"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="swiper-wrapper video_daily"]/a/@href|'
                                   '//a[@class="item"]/@href|//a[@class="title"]/@href|'
                                   '//div[@class="lb_lists_container"]/div/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        if "InsightReport" in response.url:
            title = response.xpath('//div[@class="top-title-text-wrapper"]/span/text()').extract_first(default="")
        elif "Daily/2022" in response.url:
            title = response.xpath('//div[@class="d_title"]//h1/text()').extract_first(default="")
        else:
            title = response.xpath('//article[@class="main_area"]/h1/text()|'
                                   '//div[@class="mt20 mb20"]/text()').extract_first(default="")
        return title.strip().replace('\u3000', '') if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "InsightReport" in response.url:
            time_ = response.xpath('//div[@class="mt20 mb20"]/text()').extract_first()
        elif "Daily/2022" in response.url:
            time_ = response.xpath('//div[@class="d_title"]/time/text()').extract_first()
        else:
            time_ = response.xpath(
                '//div[@class="time"]/text()|//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        if "InsightReport" or "Daily/2022" in response.url:
            return tags_list
        else:
            tags = response.xpath('//div[@class="hashtags flexbox flexwrap"]/a/text()').extract()
            if tags:
                for tag in tags:
                    if tag.strip():
                        tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//article[@class="main_area"]//img|//div[@class="img_wrapper"]/img|'
                                  '//article[@class="main_area"]//div[@class="img_wrap"]/img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//article[@class="main_area"]/*|//div[@class="main_article imgViewer"]/*|'
                                   '//div[contains(@class,"_layout_")]/*|//article[@class="main_area"]/p|'
                                   '//div[@class="insight_report_detail_content"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "h4", "div", "b"]:
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
            oneCons = "".join(cons).strip().replace('\r', '').replace('\n', '').replace('\xa0', '')
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('./@src').extract_first()
        if img.startswith("data:image/gif;base64"):
            return {}
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
        videoUrl = news_tag.xpath("").extract_first()
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
