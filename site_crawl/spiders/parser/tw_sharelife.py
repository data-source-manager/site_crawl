import json
import time
from urllib.parse import urljoin

import scrapy

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


class TwSharelifeParser(BaseParser):
    name = 'sharelife'
    
    # 站点id
    site_id = "ba12fec6-8c18-4186-9eca-6cfd8c38b789"
    # 站点名
    site_name = "台湾旅行趣"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "ba12fec6-8c18-4186-9eca-6cfd8c38b789", "source_name": "台湾旅行趣", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e700b55a-7607-11ed-ad4d-d4619d029786", "地方新闻", "https://taiwan.sharelife.tw/api/locate/getMoreResult?PAGESIZE=18&PAGEINDEX=1&artiClass=&placeCounty=&placeTown=&artiType=1&site_id=7", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = json.loads(response.text).get("data")
        if news_urls:
            for news_url in news_urls:
                article_id = news_url.get('data_id')
                yield f'https://taiwan.sharelife.tw/api/locate/byAID?AID={article_id}&site_id=7&authcode=&UserID=0'

    def get_title(self, response) -> str:
        title = json.loads(response.text).get('arti_m_title')
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:

        time_ = json.loads(response.text).get('publish_dt')
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//meta[@name="keywords"]/@content').extract()
        if tags:
            if "," in tags:
                tags = tags.split(',')

            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = json.loads(response.text)
        con_set = set()
        if news_tags:
            if news_tags.get("arti_ex"):
                if news_tags.get('arti_ex') not in con_set:
                    con_set.add(news_tags.get('arti_ex'))
                    content.append({
                        "data": news_tags.get('arti_ex'),
                        "type": "text"
                    })
            if news_tags.get('a_f_name'):
                if news_tags.get('a_f_name') not in con_set:
                    con_set.add(news_tags.get('a_f_name'))
                    img_url = urljoin(response.url, news_tags.get('a_f_name'))
                    content.append(
                        {"type": "image",
                         "name": '',
                         "md5src": self.get_md5_value(img_url) + '.jpg',
                         "description": '',
                         "src": img_url
                         })
            if news_tags.get('arti_cont'):
                html = scrapy.Selector(text=news_tags.get('arti_cont'))
                for con in html.xpath('//text()|'
                                      '//img'):
                    if type(con.root) == str:
                        if con.root.strip() and con.root.strip() not in con_set:
                            con_set.add(con.root.strip())
                            content.append({
                                "data": con.root.strip(),
                                "type": "text"
                            })
                    else:
                        if con.root.tag == "img" and con.root.tag not in con_set:
                            con_set.add(con.root.tag)
                            img_dict = self.parse_single_img(response, con)
                            if img_dict:
                                content.extend(img_dict)
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
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
