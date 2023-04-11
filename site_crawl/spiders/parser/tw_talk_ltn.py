# -*- coding: utf-8 -*-
# update:(liyun:2023-01-13) -> 新增板块与影音板块的解析代码
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwTalkParser(BaseParser):
    name = 'talk'
    
    # 站点id
    site_id = "e9056078-e0be-47e1-b01f-9b2dec509dc4"
    # 站点名
    site_name = "自由时报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e9056078-e0be-47e1-b01f-9b2dec509dc4", "source_name": "自由时报", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b7a8a-fe6f-11ec-a30b-d4619d029786", "国际", "https://news.ltn.com.tw/list/breakingnews/world", "政治"),
            ("f520ecd2-07a8-5396-9510-788613edeb94", "影音", "", "政治"),
            ("c7fff60c-c4b8-4b01-8bcb-f1b59ec4e53b", "影音/官我什么事", "https://video.ltn.com.tw/list/PLu6it9R0AYTLxehLEgikYOStIzS5CZuRJ", "政治"),
            ("75edf2c8-cb61-4c1f-a53a-a938dceb9fde", "影音/放眼国际", "https://video.ltn.com.tw/list/PLI7xntdRxhw14XV5_S5ivw_Um2hhecH8m", "政治"),
            ("b24e1750-3f64-4496-bcc4-af68970789f1", "影音/政治风向球", "https://video.ltn.com.tw/list/PLI7xntdRxhw3f4pUhXV0L2ve5j1Ztthf_", "政治"),
            ("b0c22282-7218-11ed-a54c-d4619d029786", "政治", "https://news.ltn.com.tw/list/breakingnews/politics", "政治"),
            ("4a8b7a30-fe6f-11ec-a30b-d4619d029786", "评论", "", "政治"),
            ("7c3cb632-587e-4edc-bcae-421d7b5fcf00", "评论/专论", "https://talk.ltn.com.tw/list/9", "政治"),
            ("97bc2b5f-3cfa-4d5a-a657-a6c10e17ad2e", "评论/教育大小声", "https://talk.ltn.com.tw/list/19", "政治"),
            ("f0af7e40-b9c3-4bbe-b6d8-9641b4d9966d", "评论/社论", "https://talk.ltn.com.tw/list/8", "政治"),
            ("dfa5442b-e811-493d-8469-1a15551246c5", "评论/自由共和国", "https://talk.ltn.com.tw/list/7", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "e9056078-e0be-47e1-b01f-9b2dec509dc4"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@class="tit"]/@href|//ul[@class="listbox"]/li/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin("https://video.ltn.com.tw/", news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="author"]/@content').extract()
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
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="text"]/*|'
                                   '//div[contains(@class,"text boxTitle boxText")]/*')
        if news_tags:
            for news_tag in news_tags:
                break_point = "".join(news_tag.xpath(".//text()").extract())
                if "APP看新聞" in break_point or "訂閱YouTube" in break_point:
                    break
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    if news_tag.xpath(".//img").extract():
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)
                    video = news_tag.xpath("./iframe/@src").extract_first()
                    if video:
                        if "youtube" in video:
                            con_video = self.parse_media(response, news_tag)
                            if con_video:
                                content.append(con_video)
                    else:
                        text_dict = self.parse_text(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                if news_tag.root.tag == "div":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)
                if news_tag.root.tag == "blockquote":
                    for x in news_tag.xpath("./p"):
                        text_dict = self.parse_text(x)
                        if text_dict:
                            content.extend(text_dict)

        if content:
            return content
        # 解析影音板块数据
        # 解析视频(youtube)
        video_tag = response.xpath('//div[@id="art_video"]')
        if video_tag:
            video_url = f'{"https://www.youtube.com/embed/"}{video_tag.attrib.get("data-ytid", "")}'
            content.append({
                "type": "video",
                "src": video_url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_url) + ".mp4"
            })
        # 解析正文
        for tag in response.xpath('//div[@class="text boxTitle"]/*|//div[@class="photo"]/a'):
            if tag.root.tag in ["p", "span", "h2", "h3"]:
                text = ' '.join(tag.xpath(".//text()").extract()).strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag == "a":
                src = tag.attrib.get("href", "").strip()
                suffix = src.split(".")[-1].lower()
                if suffix in ["jpg", "png", "jpeg"]:
                    content.append({
                        "type": "image",
                        "name": None,
                        "md5src": self.get_md5_value(src) + f'.{suffix}',
                        "description": tag.attrib.get("title").strip(),
                        "src": src
                    })
            else:
                pass

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-tw"

    def parse_text(self, news_tag) -> list:
        """"
            可以对一个标签下存在多个段落进行解析
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if "請繼續往下閱讀" in x.strip():
                    return []
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
        img = news_tag.xpath('.//img/@data-src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//img/@alt').extract()).strip(),
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
        videoUrl = news_tag.xpath("./iframe/@src").extract_first()
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
