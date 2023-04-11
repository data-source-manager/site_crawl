# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class CN_81Parser(BaseParser):
    name = 'cn_81'
    
    # 站点id
    site_id = "d22492c5-a69c-4105-96f8-4eed10c1c84b"
    # 站点名
    site_name = "中国军网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "d22492c5-a69c-4105-96f8-4eed10c1c84b", "source_name": "中国军网", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("dd70a986-bacf-4f9c-9a33-93fa37a16435", "H5", "http://www.81.cn/syjdt/node_76066.htm", "政治"),
            ("5889f091-6c8a-407e-bfc6-14b877c60749", "兵器", "http://www.81.cn/bq/index.htm", "政治"),
            ("edcf59b4-6702-450d-b8e1-d72286db95bd", "军史", "http://www.81.cn/j-s/index.htm", "政治"),
            ("9da33f31-91cd-41e1-8135-e66294db5721", "军委", "http://www.81.cn/jw/index.htm", "政治"),
            ("1d458986-5191-4d21-b66f-403408f1ee75", "军校", "http://www.81.cn/jx/index.htm", "政治"),
            ("86eafcb6-f220-4a52-ac6b-a6a00a3981f5", "动员", "http://www.81.cn/dy/index.htm", "政治"),
            ("4a8e0f34-fe6f-11ec-a30b-d4619d029786", "发言人", "http://www.81.cn/fb/index.htm", "政治"),
            ("ccd4677d-60a4-40bf-b7ea-8c622c8e0ce3", "备战", "http://www.81.cn/bz/index.htm", "政治"),
            ("40dd3731-8c10-4117-9468-32f8956f2936", "外军", "http://www.81.cn/w-j/index.htm", "政治"),
            ("0a45a499-888b-4980-8f04-ec91258a31be", "女兵", "http://www.81.cn/nb/index.htm", "政治"),
            ("c1ab64df-5c77-497d-8a26-f946454f980e", "学习", "http://www.81.cn/xx/index.htm", "政治"),
            ("12c45b77-b230-4f4b-8b3d-4b0715ca5887", "战区", "http://www.81.cn/zq/index.htm", "政治"),
            ("80161c92-9774-4638-b497-5fa640ad67d7", "战支", "http://www.81.cn/zz/index.htm", "政治"),
            ("c42c176f-7cf0-4ef6-a413-b4da7ac03173", "文化", "http://www.81.cn/wh/index.htm", "政治"),
            ("7b2a2324-14ef-455e-bd6c-cd39ca0ad588", "时事", "http://www.81.cn/ss/index.htm", "政治"),
            ("641f2bad-e5d3-40ce-a206-4ae3b85fa429", "武警", "http://www.81.cn/wj/index.htm", "政治"),
            ("d19bbeac-4e95-4f98-b761-a36979b60a59", "海军", "http://www.81.cn/hj/index.htm", "政治"),
            ("58650c44-b368-4202-91fa-af4c3877fbf1", "火箭军", "http://www.81.cn/hjj/index.htm", "政治"),
            ("c545856b-06d6-40f0-8bcb-00398289b95f", "特战", "http://www.81.cn/tz/index.htm", "政治"),
            ("98d4c24c-6855-4a41-9e7c-eff231571fc2", "理论", "http://www.81.cn/ll/index.htm", "政治"),
            ("7cf6ee71-7f97-447c-8eae-63402bff7c68", "空军", "http://www.81.cn/kj/index.htm", "政治"),
            ("1a84f681-50f2-48ce-b4f8-1b30c0932527", "空天", "http://www.81.cn/kt/index.htm", "政治"),
            ("cef59d4a-cae2-4d79-ae02-ace933be2684", "维和", "http://www.81.cn/vh/index.htm", "政治"),
            ("602c1dcc-88ac-4cbc-9705-79b444ce27d7", "联勤", "http://www.81.cn/l-b/index.htm", "政治"),
            ("1dd079b0-a5a5-40df-92f5-4739b983886f", "要闻", "http://www.81.cn/yw/index.htm", "政治"),
            ("4a8e0ebc-fe6f-11ec-a30b-d4619d029786", "评论", "http://www.81.cn/pl/index.htm", "政治"),
            ("7faa2764-3ffe-41f6-a1fe-4d54e2c3e619", "边关", "http://www.81.cn/bg/index.htm", "政治"),
            ("43203c27-80de-4a30-96d5-60c1e0d36d83", "陆军", "http://www.81.cn/lj/index.htm", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "d22492c5-a69c-4105-96f8-4eed10c1c84b"
        self.Dict = {}
        self.page_set = set()

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//ul[@id='main-news-list']/li[@class='article']/a/@href|"
                                   '//ul[@id="main-news-list"]/li//a/@href').extract() or []
        if news_urls:
            for news_url in news_urls:
                url = urljoin(response.url, news_url)
                if "www.news.cn" not in url:
                    yield url

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='article-header']/h1/text()").extract_first(default="") or ""
        if not title:
            title = response.xpath("//h2/text()").extract_first(default="") or ""
        news_issue_title = title.strip()
        if "丨" in news_issue_title:
            news_issue_title = news_issue_title.split("丨")[1]
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        author_Strs = response.xpath("//meta[@name='reporter']/@content").extract_first()
        if author_Strs:
            if "、" in author_Strs:
                authors = author_Strs.split("、")
            elif " " in author_Strs:
                authors = author_Strs.split(" ")
                for author_a in authors:
                    authors.append(author_a)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//small/i[@class='time']/text()|"
                                  '//div[contains(@class,"artichle-info")]/p/span[last()]/text()|'
                                  '//div[@class="video-info-right"]/p[last()]/small/text()').extract_first()
        if Date_str:
            if "发布：" in Date_str:
                Date_str = Date_str.replace("发布：", "")
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@id='article-content']/*|//div[@class=' m-t-list']/*|"
                                   '//div[@style="TEXT-ALIGN: left"]/p|//ul[@class="row m-t-list"]/*|'
                                   '//div[@style="TEXT-ALIGN: left"]/center|//div[@class="cm-player"]/video|'
                                   '//div[@class="video-info"]//a[@id="download"]|'
                                   '//div[@id="main-news-list"]/section/section/*|'
                                   '//div[@id="main-news-list"]/p|'
                                   '//div[@id="main-news-list"]/div/p|'
                                   '//ul[@id="main-news-list"]//p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p", "font", "section"]:
                    img_dict = self.parse_img(response, news_tag.xpath(".//img"))
                    if img_dict:
                        content.append(img_dict)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                if news_tag.root.tag == "center":
                    if news_tag.xpath(".//video"):
                        video_dict = self.parse_media(response, news_tag.xpath(".//video"), media_type="mp4")
                        if video_dict:
                            content.append(video_dict)
                    elif news_tag.xpath(".//img"):
                        img_dict = self.parse_img(response, news_tag.xpath(".//img"))
                        if img_dict:
                            content.append(img_dict)
                if news_tag.root.tag == "video" or news_tag.root.tag == "a":
                    con_media = self.parse_media(response, news_tag, media_type="mp4")
                    if con_media:
                        content.append(con_media)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

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

    def parse_img(self, response, news_tag):
        img = news_tag.xpath('./@src').extract_first()
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
        file_src = urljoin(response.url, news_tag.xpath("").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag, media_type):
        videoUrl = news_tag.xpath("./@src").extract_first()
        videoUrl = videoUrl if videoUrl else "http://tv.81.cn/"+re.findall("media=(.*?).mp4",response.text)[0]
        video_dic = {}

        if videoUrl:
            suffix = f".{media_type}"
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
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        if self.Dict.get(response.url):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        repost_source_str = response.xpath("//div[@class='info']/span[1]/text()").get()
        if repost_source_str:
            self.Dict[response.url] = repost_source_str
            repost_source = repost_source_str.replace("来源：", "")
        return repost_source
