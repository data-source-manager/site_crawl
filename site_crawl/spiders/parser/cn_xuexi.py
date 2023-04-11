# -*- coding: utf-8 -*-
import json
import re
import time
from urllib.parse import urljoin

import requests
from scrapy import Selector

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class CN_xuexiParser(BaseParser):
    name = 'cn_xuexi'
    
    # 站点id
    site_id = "5c5c2d3c-3f35-422e-ad8c-57b91bc34bec"
    # 站点名
    site_name = "学习强国"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "5c5c2d3c-3f35-422e-ad8c-57b91bc34bec", "source_name": "学习强国", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("1c04520e-f4f6-4ba0-8c70-63aec41ad4b6", "习近平同期声", "https://www.xuexi.cn/fcfa179537ceda0bfbee9727591a102c/4ec8b5c5df17c32984741d967609a967.html", "政治"),
            ("2bc35d66-0de7-4cd7-ab2b-d0e52a700f34", "习近平强军思想研究", "https://www.xuexi.cn/260484980c8d612dfeb2255e8d560107/9a3668c13f6e303932b5e0e100fc248b.html", "政治"),
            ("6b39d336-b885-485c-9e98-64dccb571eab", "习近平文汇", "https://www.xuexi.cn/5c90534c80d14c060d6683fa960e3676/82573c005c024095037d2186a02244cb.html", "政治"),
            ("666d2ca9-be28-480c-99d3-7b977a9a189c", "习近平重要讲话", "https://www.xuexi.cn/588a4707f9db9606d832e51bfb3cea3b/9a3668c13f6e303932b5e0e100fc248b.html", "政治"),
            ("4b47ea60-35c2-4c89-b3b6-246df104d1e1", "头条新闻", "https://www.xuexi.cn/72ac54163d26d6677a80b8e21a776cfa/9a3668c13f6e303932b5e0e100fc248b.html", "政治"),
            ("02c65899-eb69-4bb6-bb78-51ccbe35a411", "学习时评", "https://www.xuexi.cn/d05cad69216e688d304bb91ef3aac4c6/9a3668c13f6e303932b5e0e100fc248b.html", "政治"),
            ("8a4b20b9-8361-4791-a306-8fd78feb63e7", "强军时评", "https://www.xuexi.cn/1abd1ef290d0b162b2cf9f6ab72487e8/9a3668c13f6e303932b5e0e100fc248b.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}
        self.real_url_dict = {
            "588a4707f9db9606d832e51bfb3cea3b": "https://www.xuexi.cn/lgdata/132gdqo7l73.json",
            "d05cad69216e688d304bb91ef3aac4c6": "https://www.xuexi.cn/lgdata/1ap1igfgdn2.json",
            "260484980c8d612dfeb2255e8d560107": "https://www.xuexi.cn/lgdata/12lm260c37e.json",
            "1abd1ef290d0b162b2cf9f6ab72487e8": "https://www.xuexi.cn/lgdata/1j2fuv9rs7e.json",
            "5c90534c80d14c060d6683fa960e3676": "https://www.xuexi.cn/lgdata/5c90534c80d14c060d6683fa960e3676/82573c005c024095037d2186a02244cb.json",
            "72ac54163d26d6677a80b8e21a776cfa": "https://www.xuexi.cn/lgdata/1crqb964p71.json",
            "fcfa179537ceda0bfbee9727591a102c": "https://www.xuexi.cn/lgdata/18f0lgegu7l.json"
        }

    def parse_list(self, response) -> list:
        flag_ = re.findall("https://www.xuexi.cn/(.*?)/\S+.html", response.url)
        if flag_:
            news_url = self.real_url_dict.get(flag_[0])
            if "5c90534c80d14c060d6683fa960e3676" in news_url:
                pagedata = requests.get(news_url).json()
                textList = pagedata['pageData']['textList']
                tem_url = 'https://www.xuexi.cn/lgdata/{id}.json'
                for board_url in textList[:20]:
                    link = board_url['itemId']
                    if len(link) % 3 == 0:
                        index = int(len(link) / 3)
                    else:
                        index = int((len(link) + 1) / 3)
                    news_url = tem_url.format(id=link[:index])

            JosnData = requests.get(news_url).json()
            for item in JosnData:
                demo_url = item['url']
                try:
                    rsp_url = f"https://boot-source.xuexi.cn/data/app/{demo_url.split('id=')[-1]}.js"
                except:
                    rsp_url = ""
                self.Dict[rsp_url] = {"author": item['editor'], "title": item['title'],
                                      "publish_time": item['publishTime'],
                                      "source": item['showSource'], "demo_url": demo_url}
                yield {
                    "origin_url": demo_url,
                    "real_url": rsp_url
                }

    def get_title(self, response) -> str:
        title = self.Dict[response.url].get("title")
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_a = self.Dict[response.url].get("author")
        if author_a:
            authors.append(author_a.lstrip("[\"").rstrip("\"]"))
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = self.Dict[response.url].get("publish_time")
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        jsondata = json.loads(response.text.lstrip("callback(").rstrip(")"))
        audio = jsondata.get("audios")
        if audio:
            audio_url = audio[0].get("audio_storage_info")[0].get("url")
            if audio_url:
                audio_dic = {
                    "type": "audio",
                    "src": audio_url,
                    "name": None,
                    "description": None,
                    "md5src": self.get_md5_value(audio_url) + ".mp3"
                }
                content.append(audio_dic)
        content_html = jsondata.get('content')
        if content_html:
            contents_selctor = Selector(text=content_html)
            for con in contents_selctor.xpath("//p"):
                con_dict = self.parseOnetext(con)
                if con_dict:
                    content.extend(con_dict)
        image = jsondata.get("image")
        if image:
            for img in jsondata['image']:
                img_src = {"type": "image",
                           "name": None,
                           "md5src": self.get_md5_value(img['url']) + '.jpg',
                           "description": img['desc'] or None,
                           "src": img['url']}
                content.append(img_src)
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

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

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        if self.Dict[response.url].get("source"):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        if self.Dict[response.url].get("source"):
            repost_source = self.Dict[response.url].get("source")
        return repost_source
