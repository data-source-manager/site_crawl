# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper

"""
    模版
"""


class KrEaiParser(BaseParser):
    name = 'eai'
    
    # 站点id
    site_id = "cec258d9-786f-44ef-808c-21e82e2a7522"
    # 站点名
    site_name = "东亚研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "cec258d9-786f-44ef-808c-21e82e2a7522", "source_name": "东亚研究所", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e9f0ae61-5c12-06f9-8979-b569f8f4d8c5", "专题", "", "政治"),
            ("4a8c4a1e-fe6f-11ec-a30b-d4619d029786", "专题/朝鲜问题", "http://www.eai.or.kr/new/ko/project/list.asp?code=98", "政治"),
            ("4a8c4b9a-fe6f-11ec-a30b-d4619d029786", "专题/未来的创新和治理", "http://www.eai.or.kr/new/ko/project/list.asp?code=115", "政治"),
            ("4a8c4ab4-fe6f-11ec-a30b-d4619d029786", "专题/民主合作", "http://www.eai.or.kr/new/ko/project/list.asp?code=100", "政治"),
            ("4a8c4bd6-fe6f-11ec-a30b-d4619d029786", "专题/美国竞争与韩国战略", "http://www.eai.or.kr/new/ko/project/list.asp?code=97", "政治"),
            ("4a8c4b22-fe6f-11ec-a30b-d4619d029786", "专题/贸易、技术和能源秩序的未来", "http://www.eai.or.kr/new/ko/project/list.asp?code=107", "政治"),
            ("4a8c4a50-fe6f-11ec-a30b-d4619d029786", "专题/韩日关系的重建", "http://www.eai.or.kr/new/ko/project/list.asp?code=99", "政治"),
            ("e9255d7b-da32-5c35-3800-cdf53f2139c0", "事件", "", "政治"),
            ("3496b970-116f-4e23-8885-0f3e36b43c54", "事件/即将发送的事件", "https://www.eai.or.kr/new/ko/event/?event_type=1", "政治"),
            ("a39aa983-3082-43ee-9188-5c91966ea29c", "事件/整个事件", "https://www.eai.or.kr/new/ko/event/?event_type=2", "政治"),
            ("a8034f5f-95dc-bc71-446c-bf4a9114c96e", "出版", "", "政治"),
            ("9242ccab-b46a-4216-801b-4ed2cef93c36", "出版/JEAS", "http://www.eai.or.kr/new/ko/pub/jeas.asp?board=eng_jeas", "政治"),
            ("20b538a1-4198-4597-ace6-c3804e8ef104", "出版/专着", "http://www.eai.or.kr/new/ko/pub/list.asp?board=kor_book", "政治"),
            ("0d546788-ab4a-4df7-b453-37c411b01220", "出版/多媒体", "http://www.eai.or.kr/new/ko/pub/list.asp?board=kor_multimedia", "政治"),
            ("0f77cef7-e606-45c4-bbf1-aae0cce6c2b7", "出版/工作文件", "http://www.eai.or.kr/new/ko/pub/list.asp?board=kor_workingpaper", "政治"),
            ("31409712-0042-4f17-ae1e-653d29f1e1bd", "出版/特别报道", "http://www.eai.or.kr/new/ko/pub/list.asp?board=kor_special", "政治"),
            ("ba80a15b-c2b6-7dcb-fbe7-5aeb6aeadc16", "出版/评论", "", "政治"),
            ("3695e886-0255-4cd5-87ac-4ea2376a41f6", "出版/评论/问题简报", "http://www.eai.or.kr/new/ko/pub/list.asp?board=kor_issuebriefing", "政治"),
            ("4a8c4c12-fe6f-11ec-a30b-d4619d029786", "所有出版物", "http://www.eai.or.kr/new/ko/pub/list.asp?board=kor_commentary", "政治"),
            ("4a8c49d8-fe6f-11ec-a30b-d4619d029786", "新闻稿", "https://eai.or.kr/new/ko/news/notice.asp?board=kor_eaiinmedia&page=1", "政治"),
            ("b957a695-2e05-bcb3-8601-dc3f5a54b0ff", "项目", "", "政治"),
            ("57d7b336-0eaa-4b78-8de6-e681583892a6", "项目/名主合作", "http://www.eai.or.kr/new/ko/project/list.asp?code=100", "政治"),
            ("ed84529e-a6f2-495a-8898-beae8983f944", "项目/未来创新与治理", "http://www.eai.or.kr/new/ko/project/list.asp?code=115", "政治"),
            ("40038727-b4e2-48ac-8dae-2eb4d1641833", "项目/美中竞争与韩国战略", "http://www.eai.or.kr/new/ko/project/list.asp?code=97", "政治"),
            ("b6fefe20-43c4-412d-ac47-16dde25b99be", "项目/读朝鲜", "http://www.eai.or.kr/new/ko/project/list.asp?code=98", "政治"),
            ("5d6e24e2-e527-4d01-bd35-3a6892fda0dc", "项目/贸易，技术和能源的未来", "http://www.eai.or.kr/new/ko/project/list.asp?code=107", "政治"),
            ("558a9480-78ce-4cfa-a483-2e85f2c668cc", "项目/重建韩日关系", "http://www.eai.or.kr/new/ko/project/list.asp?code=99", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//p[@class="subject"]/a/@href|'
                                   '//div[@class="__issueList"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//p[@class="subject"]/text()|'
                               '//div[@class="title"]/h1/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//ul[@class="desc"]/li[2]/text()').extract_first()
        if authors:
            authors = authors.split(" ")[0]
            if authors.strip():
                author_list.append(authors.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//ul[@class="desc"]/li[1]/text()|'
                               '//p[@class="m_hj2"]/text()').extract_first()
        if time_:
            if "VOL." in time_:
                return "9999-01-01 00:00:00"
            if "|" in time_:
                time_ = time_.split('|')[-1]
            time_ = datetime.strptime(time_.strip(), "%Y-%m-%d")
            return datetime_helper.parseTimeWithOutTimeZone(time_, site_name="东亚研究所")

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@class="keywords"]/a/p/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.replace("#", "").strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="cont"]/*|'
                                   '//div[@class="list"]/div/*|'
                                   '//div[@class="cont"]/ul|'
                                   '//div[@class="list"]/div/div/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    if news_tag.xpath('.//img').extract():
                        con_img = self.parse_img(response, news_tag)
                        if con_img:
                            content.append(con_img)
                    else:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)

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
        img = news_tag.xpath('.//img/@src').extract_first()
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
