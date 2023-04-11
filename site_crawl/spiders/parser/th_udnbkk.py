# -*- coding: utf-8 -*-
# update: [liyun:2023-01-17] -> 板块核对与修正
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TH_udnbkkParser(BaseParser):
    name = 'th_udnbkk'
    
    # 站点id
    site_id = "abda57d0-2bcc-45cf-a73e-096f024a81bb"
    # 站点名
    site_name = "泰国世界日报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "abda57d0-2bcc-45cf-a73e-096f024a81bb", "source_name": "泰国世界日报", "direction": "th", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8d0efe-fe6f-11ec-a30b-d4619d029786", "国际", "http://www.udnbkk.com/portal.php?mod=list&catid=61", "政治"),
            ("a6e3c313-2d3f-46f7-aa55-33be16856aa1", "国际/东南亚新闻", "http://www.udnbkk.com/portal.php?mod=list&catid=63", "政治"),
            ("c11105f8-74bf-4ff5-ab7e-d1bd79794780", "国际/台湾新闻", "http://www.udnbkk.com/portal.php?mod=list&catid=85", "政治"),
            ("535d33a0-3295-4a3b-a3ac-ec1e4b4d3fec", "国际/国际新闻", "http://www.udnbkk.com/portal.php?mod=list&catid=137", "政治"),
            ("a80b81cd-6977-4bad-bc18-c3819f93f82c", "国际/大陆新闻", "http://www.udnbkk.com/portal.php?mod=list&catid=131", "政治"),
            ("2139cd54-dcef-4828-b317-c866642c7eda", "国际/焦点话题", "http://www.udnbkk.com/portal.php?mod=list&catid=160", "政治"),
            ("4a8d0da0-fe6f-11ec-a30b-d4619d029786", "政治", "http://www.udnbkk.com/portal.php?mod=list&catid=46", "政治"),
            ("fd0e3f4f-ec8d-4488-bfbe-f9a514a2f1dd", "政治/泰国政治", "http://www.udnbkk.com/portal.php?mod=list&catid=132", "政治"),
            ("76e2df24-6f2c-4b6f-96ba-634eb9457b54", "政治/社论", "http://www.udnbkk.com/portal.php?mod=list&catid=158", "政治"),
            ("4a8d0e18-fe6f-11ec-a30b-d4619d029786", "社会", "http://www.udnbkk.com/portal.php?mod=list&catid=50", "其他"),
            ("72a74b39-9b2b-4392-8ddf-c0d19dbe86a3", "社会/泰国社会", "http://www.udnbkk.com/portal.php?mod=list&catid=99", "其他"),
            ("4a8d0e90-fe6f-11ec-a30b-d4619d029786", "财经", "http://www.udnbkk.com/portal.php?mod=list&catid=51", "经济"),
            ("9a121fc0-d97b-491a-9be0-3570379bba6e", "财经/泰国经济", "http://www.udnbkk.com/portal.php?mod=list&catid=105", "经济"),
            ("e64d7e29-e44b-4605-985c-806dc214aa8b", "财经/泰国股市", "http://www.udnbkk.com/portal.php?mod=list&catid=74", "经济"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "abda57d0-2bcc-45cf-a73e-096f024a81bb"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="bb_divt"]/a/@href').extract() or []
        for url in news_urls:
            yield urljoin(response.url, url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        authors = []
        auhtor_strs = response.xpath("//p[@class='xg1']/a/text()").get()
        if auhtor_strs:
            authors.append(auhtor_strs)
        return authors

    def get_pub_time(self, response) -> str:
        Date_str = response.xpath("//p[@class='xg1']/text()[1]").get()
        if Date_str:
            dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//td[@id="article_content"]/*|//td[@id="article_content"]//img'
        ):
            # 解析文本
            if tag.root.tag in ["p", "div"]:
                text = " ".join(tag.xpath(".//text()").extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            # 解析图像
            elif tag.root.tag == "img":
                img_url = urljoin(response.url, tag.attrib.get("src", "").split("?")[0].strip())
                suffix = img_url.split(".")[-1].lower()
                if suffix not in ['jpg', 'png', 'jpeg']:
                    continue
                img_url and content.append({
                    "type": "image",
                    "src": img_url,
                    "md5src": self.get_md5_value(img_url) + f'.{suffix}',
                    "name": None,
                    "description": tag.attrib.get("alt", "").strip(),
                })
            else:
                pass
        # 移除无关字段
        (content and content[0].get("data", "").startswith("读新闻")) and content.pop(0)
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
        video_src = news_tag.xpath("./source/@src").extract_first()
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(video_src) + ".mp4"
        }
        return video_dic

    def get_like_count(self, response) -> int:
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        comment_count_str = response.xpath("//p[@class='xg1']/text()[last()]").get()
        if comment_count_str:
            comment_count = int(comment_count_str.replace("评论:", "").strip())
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        read_count_str = response.xpath("//p[@class='xg1']/em[@id='_viewnum']/text()").get()
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
