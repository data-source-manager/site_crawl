# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from lxml import etree

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    站点解析模版
"""


class TwAecParser(BaseParser):
    name = 'aec'
    
    # 站点id
    site_id = "188b4e4d-ba65-3070-9a5c-e0728c27ed15"
    # 站点名
    site_name = "原子能委员会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "188b4e4d-ba65-3070-9a5c-e0728c27ed15", "source_name": "原子能委员会", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("b0c2180a-7218-11ed-a54c-d4619d029786", "动态讯息", "https://www.aec.gov.tw/news/newsboard.html", "政治"),
            ("d209459a-b604-a3a9-ef6a-2def0834ce5c", "国际核能新闻", "https://www.aec.gov.tw/%E6%96%BD%E6%94%BF%E8%88%87%E6%B3%95%E8%A6%8F/%E5%9C%8B%E9%9A%9B%E5%90%88%E4%BD%9C/%E5%9C%8B%E9%9A%9B%E7%9E%AD%E6%9C%9B/%E5%9C%8B%E9%9A%9B%E6%A0%B8%E8%83%BD%E6%96%B0%E8%81%9E--2_16_18_88.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "newsboard" in response.url:
            news_urls = response.xpath('//a[@class="styleTitle"]/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)
        else:
            news_urls = response.xpath('//div[@id="page-html"]/a')
            if news_urls:
                for news_url in news_urls:
                    rsp_url = news_url.xpath('./@href').get()
                    rsp_title = news_urls.xpath('./text()').get()
                    url = urljoin(response.url, rsp_url)
                    self.Dict[url] = {'title': rsp_title}
                    yield url

    def get_title(self, response) -> str:
        if "newsdetail" in response.url:
            title = response.xpath('//meta[@name="dc.title"]/@content').extract_first(default="")
            return title.strip() if title else ""
        else:
            title = self.Dict[response.url]['title']
            return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        if "newsdetail" in response.url:
            time_ = response.xpath('//div[@class="col-md-8 mb-2"]/small/text()').extract_first()
            if time_:
                pub_time = datetime_helper.fuzzy_parse_timestamp(time_.replace('更新時間：', "").strip())
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
            return "9999-01-01 00:00:00"
        elif '.pdf' in response.url:
            return "9999-01-01 00:00:00"
        else:
            time_ = response.xpath('//meta[@name="dc.coverage.t.min"]/@content').extract_first()
            if time_:
                pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
                return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        if ".pdf" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
        else:
            news_tags = response.xpath('//div[@class="bk15"]//text()|//div[@id="page-html"]/table|'
                                       '//div[@class="bk15"]/*|'
                                       '//td[@class="bk15"]/*|'
                                       '//td[@class="bk15"]|'
                                       '//td[@class="bk15"]/text()')
            if news_tags:
                for news_tag in news_tags:
                    if type(news_tag.root) == str:
                        if news_tag.root.strip():
                            content.append({
                                "data": news_tag.root.strip(),
                                "type": "text"
                            })
                    else:
                        if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                            text_dict = self.parse_text(news_tag)
                            if text_dict:
                                content.extend(text_dict)

                        if news_tag.root.tag == "img":
                            con_img = self.parse_img(response, news_tag)
                            if con_img:
                                content.extend(con_img)
                        if news_tag.root.tag in "table":
                            html_str = etree.tostring(news_tag.root, encoding="utf-8").decode("utf-8")
                            content.append({'data': html_str, 'type': 'text'})

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

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        imgs = news_tag.xpath('.//img')

        img_list = []

        if imgs:
            for img in imgs:
                img_url = urljoin(response.url, img.xpath("./@src").extract_first())

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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
