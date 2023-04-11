# -*- coding: utf-8 -*-
# fix: [liyun:2023-01-07] -> 标题解析异常
# update: [liyun:2023-01-16] -> 新增板块并修正解析代码
# update: [yasuo:2023-02-06] -> 新增板块：政治/Yahoo论坛/政事观察站、政治/Yahoo论坛/全球化视野

import json
import re
import time
from html import unescape
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TW_yahooParser(BaseParser):
    name = 'tw_yahoo'
    
    # 站点id
    site_id = "68a069a6-ad49-4489-9207-64f168ee222a"
    # 站点名
    site_name = "Yahoo奇摩"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "68a069a6-ad49-4489-9207-64f168ee222a", "source_name": "Yahoo奇摩", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("6ca24e74-1fd1-44d6-b7b6-2a0253692018", "Yahoo特派", "https://tw.stock.yahoo.com/reporter", "政治"),
            ("163a702f-3d80-4f29-b7e0-dc396bdac9aa", "世新大学", "https://tw.news.yahoo.com/search?p=%E4%B8%96%E6%96%B0%E5%A4%A7%E5%AD%B8+%E6%B0%91%E8%AA%BF&fr=news", "政治"),
            ("7c8680ad-fc05-47d5-834d-2b94cc8a61f7", "业界动态", "https://tw.news.yahoo.com/industry/", "政治"),
            ("4a8c3c40-fe6f-11ec-a30b-d4619d029786", "国际", "https://tw.news.yahoo.com/world/", "政治"),
            ("2bc7663b-0253-43be-ae92-fa58ffdf60cc", "国际/BBC中文", "https://tw.news.yahoo.com/bbc_trad_chinese_tw_489--%E6%89%80%E6%9C%89%E9%A1%9E%E5%88%A5/archive", "政治"),
            ("1b33e594-3d65-4343-9041-c6156b296d38", "国际/Yahoo国际通", "https://tw.news.yahoo.com/global_videos_163--%E6%89%80%E6%9C%89%E9%A1%9E%E5%88%A5/archive/", "政治"),
            ("5cee18c6-a57e-418e-94e3-0667e3eb0bbc", "国际/世界日报", "https://tw.news.yahoo.com/__60--%E6%89%80%E6%9C%89%E9%A1%9E%E5%88%A5/archive/", "政治"),
            ("e13fcd25-1340-4e5c-a30f-a63b4e4748a9", "国际/中港澳", "https://tw.news.yahoo.com/china/", "政治"),
            ("40d89f71-c3f8-4494-b042-a0bac9c2eecd", "国际/亚澳", "https://tw.news.yahoo.com/asia-australia/", "政治"),
            ("c7867c9e-a8b8-4442-853d-1ba45e3658e4", "国际/德国之声", "https://tw.news.yahoo.com/www_dw_com_641--%E6%89%80%E6%9C%89%E9%A1%9E%E5%88%A5/archive/", "政治"),
            ("870836ff-10ac-400b-9e4a-6c86a936c012", "国际/欧非", "https://tw.news.yahoo.com/euro-africa/", "政治"),
            ("685ca8b3-b15a-4a2f-a3f3-c6a073d8000c", "国际/法新社", "https://tw.news.yahoo.com/afp.cnanews.gov.tw--%E6%89%80%E6%9C%89%E9%A1%9E%E5%88%A5/archive/", "政治"),
            ("cfbdb6fb-1962-4100-adfb-1520c7a832eb", "国际/美洲", "https://tw.news.yahoo.com/america/", "政治"),
            ("ad5c9917-879d-489f-8bbe-5e183f4a7f42", "国际/路透社", "https://tw.news.yahoo.com/reuters.com.tw--%E6%89%80%E6%9C%89%E9%A1%9E%E5%88%A5/archive/", "政治"),
            ("4a8c3c90-fe6f-11ec-a30b-d4619d029786", "政治", "https://tw.news.yahoo.com/politics/", "政治"),
            ("e3af2aab-05e3-43d9-b462-d28130b19740", "政治/Yahoo论坛", "https://tw.news.yahoo.com/topic/blog", "政治"),
            ("dace700d-e5a0-4b1b-86dd-4940fced387a", "政治/Yahoo论坛/全球化视野", 'https://tw.news.yahoo.com/_td-news/api/resource/NCPListService;count=100;listId=a89c81d0-3719-11e9-bafb-4d6905fcd8e9;mrs={"w":440,"h":246,"size":{"w":440,"h":246},"shouldCrop":false};snippetCount=20;useRelativeUrl=true?bkt=news-TW-zh-Hant-TW-def&device=desktop&ecma=modern&feature=enableOlympicsModule,oathPlayer,article20,videoDocking&intl=tw&lang=zh-Hant-TW&partner=none&prid=39i8s8phu1e80&region=TW&site=news&tz=America/Los_Angeles&ver=2.3.2117&returnMeta=true', "政治"),
            ("8402c542-5b90-4e61-9ec2-475277678045", "政治/Yahoo论坛/政事观察站", 'https://tw.news.yahoo.com/_td-news/api/resource/NCPListService;count=100;listId=bae969c0-3719-11e9-a7bf-77d69197bc35;mrs={"w":440,"h":246,"size":{"w":440,"h":246},"shouldCrop":false};snippetCount=20;useRelativeUrl=true?bkt=news-TW-zh-Hant-TW-def&device=desktop&ecma=modern&feature=enableOlympicsModule,oathPlayer,article20,videoDocking&intl=tw&lang=zh-Hant-TW&partner=none&prid=0pu5qt5hu1dmq&region=TW&site=news&tz=America/Los_Angeles&ver=2.3.2117&returnMeta=true', "政治"),
            ("e6eb77ca-42ae-4921-a72c-7153bb70c587", "理财就业", "https://tw.news.yahoo.com/money-career/", "政治"),
            ("6a89a899-c800-4d73-812d-f945cd7eb855", "股市汇市", "https://tw.news.yahoo.com/stock/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = []
        # 特殊处理: Y民调板块
        if response.url == "https://tw.news.yahoo.com/poll/polllist":
            try:
                data = json.loads(re.search(r'root\.App\.main = (.+);', response.text).groups()[0])
                news_urls = [
                    f'https://tw.news.yahoo.com/poll/{poll["id"]}'
                    for poll in data["context"]["dispatcher"]["stores"]["IndexDataStore"]["indexData"]["poll"]
                    if poll["reason"] == "EXPIRED"
                ]
            except:
                # import traceback
                # print(traceback.format_exc())
                pass
            for news_url in list(set(news_urls)):
                news_url = urljoin(response.url, news_url)
                if news_url.startswith(
                        "https://tw.news.yahoo.com") and news_url != "https://tw.news.yahoo.com/topic/russia-ukraine":
                    yield news_url
        # 政事观察站、全球化视野板块
        elif response.url.startswith('https://tw.news.yahoo.com/_td-news'):
            data = response.json()
            for news_url in (f"https://tw.news.yahoo.com/{row['url']}" for row in data['data']['rows']):
                yield news_url
        else:
            news_urls = response.xpath(
                '//div[@id="Main"]//h3/a/@href|//div[@id="Main"]//li/a/@href|'
                '//div[@class="Fx(a) Mstart(20px)"]/a/@href|//a[contains(@class,"hero-item")]/@href'
            ).extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)

    # fix: liyun - 2023-01-07: 标题解析异常
    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content|'
                               '//meta[@name="twitter:title"]/@content').extract_first(default="")
        return title.strip()

    def get_author(self, response) -> list:
        author_list = []
        author_s = response.xpath("//p[text()[contains(.,'報導')]][string-length(text())<15]").get()
        if author_s:
            Author = re.findall("／(.*?)報導", author_s)
            if Author:
                author_list.extend(Author)
        author_item = response.xpath("//span[@class='caas-author-byline-collapse']/text()").get()
        if author_item:
            author_list.append(author_item)
        return author_list

    def get_pub_time(self, response) -> str:
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.xpath("//time/@datetime").extract_first() or ""
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:

        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析视频
        try:
            video_id = re.search(r'mediaItems.+?\[(.+?)\]', response.text).groups()[0]
            video_id = json.loads(unescape(video_id)).get("id")
            video_url = f'blob:https://tw.news.yahoo.com/{video_id}'
            video_id and content.append({
                "type": "video",
                "src": video_url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_url) + ".mp4"
            })
        except:
            pass
        # 解析正文数据
        for tag in response.xpath(
                '//div[@class="caas-body"]/*'
        ):
            # 解析文本
            if tag.root.tag == "p":
                text = " ".join(tag.xpath(".//text()").extract() or []).strip()
                # 检测正文结尾
                if re.match(r'(＿+)|(更多)', text):
                    break
                text and content.append({"data": text, "type": "text"})
            # 解析图像
            elif tag.root.tag == "figure":
                for img_tag in tag.xpath(".//img"):
                    img_url = img_tag.attrib.get("src", "").strip()
                    img_url and content.append({
                        "type": "image",
                        "src": img_url,
                        "md5src": self.get_md5_value(img_url) + '.jpg',
                        "name": None,
                        "description": img_tag.attrib.get("alt", "").strip(),
                    })
            elif tag.root.tag == "figure":
                for img_tag in tag.xpath(".//img"):
                    img_url = img_tag.attrib.get("src", "").strip()
                    img_url and content.append({
                        "type": "image",
                        "src": img_url,
                        "md5src": self.get_md5_value(img_url) + '.jpg',
                        "name": None,
                        "description": img_tag.attrib.get("alt", "").strip(),
                    })
            else:
                pass

        return content

    def get_detected_lang(self, response) -> str:
        return 'en'

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if '更多民視新聞報導' in x or '看影片請點我' in '＿＿＿＿＿＿＿＿' in x or \
                        '文章僅反映作者意見，不代表Yahoo奇摩立場' in x or "原文網址：" in x or "更多放言Fount Media" \
                        in x or "延伸閱讀：" in x or "「民調透明百科計畫」" in x or '＿＿＿＿＿＿＿＿＿＿＿＿＿' in x:
                    break
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, descrption_xpath=None):
        img_url = urljoin(response.url, news_tag.xpath(".//img/@src").get())
        dic = {"type": "image",
               "name": None,
               "md5src": self.get_md5_value(img_url) + '.jpg',
               "description": response.xpath(".//figcaption/text()").extract_first(),
               "src": img_url}
        return dic

    def parse_file(self, response, news_tag, description_xpath):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": news_tag.xpath(description_xpath).extract_first(),
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url, news_tag.xpath("./@src").extract_first())
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
