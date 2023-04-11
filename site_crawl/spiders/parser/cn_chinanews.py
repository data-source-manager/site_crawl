# -*- coding: utf-8 -*-
# fix: liyun - 2023-01-07 -> 异常标题修正(特殊情况)
# update:(liyun:2023-01-13) -> 新增板块

import datetime
import json
import re
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser


class CnChinanewsParser(BaseParser):
    name = 'chinanews'
    
    # 站点id
    site_id = "96c53d83-91d8-4a23-bb2a-6c23243f3c26"
    # 站点名
    site_name = "中新网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "96c53d83-91d8-4a23-bb2a-6c23243f3c26", "source_name": "中新网", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("b0c21aa8-7218-11ed-a54c-d4619d029786", "两岸", "https://channel.chinanews.com.cn/u/gn-la.shtml", "政治"),
            ("f97d4eda-f313-4f81-bbf8-eddbe98acef8", "军事", "https://channel.chinanews.com.cn/cns/cl/gn-js.shtml", "军事"),
            ("b0c219d6-7218-11ed-a54c-d4619d029786", "即时新闻", "https://www.chinanews.com.cn/scroll-news/news1.html", "政治"),
            ("d7962f55-1723-4894-847d-3074a752b25b", "国际", "https://www.chinanews.com.cn/world/", "政治"),
            ("40083cc3-a7ad-0edb-8d61-c9ca5af0f2da", "大湾区", "https://www.chinanews.com.cn/dwq/", "政治"),
            ("2e2188b8-6574-42f7-8035-f3b72ce9a4d5", "理论", "https://channel.chinanews.com.cn/u/ll.shtml", "其他"),
            ("b0c21a44-7218-11ed-a54c-d4619d029786", "要闻", "https://www.chinanews.com.cn/importnews.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "96c53d83-91d8-4a23-bb2a-6c23243f3c26"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="content_list"]/ul/li//div[@class="dd_bt"]/a/@href'
            '|//div[@class="news_list "]/ul/li//div[@class="topcon"]/a/@href'
            '|//div[@class="topcon"]/a/@href'
            '|//ul[@class="news_list_ul"]/li/a/@href'
            '|//div[@class="banner_pic"]/ul/li/a/@href'
            '|//ul[@class="focus-ul"]/li/a/@href'
            '|//div[@id="gdt"]/ul/li/a/@href'
        ).extract() or []
        if not news_urls:
            try:
                news_url_data = json.loads(re.search(r'var.+?(\[.+?\])', response.text).groups()[0])
                news_urls = [data["url"] for data in news_url_data if (isinstance(data, dict) and data.get("url"))]
            except:
                pass
        for news_url in list(set(news_urls)):
            if news_url.endswith("index.shtml"):
                continue
            yield urljoin(response.url, news_url)

    # fix: liyun - 2023-01-07 -> 异常标题修正(特殊情况)
    def get_title(self, response) -> str:
        title = response.xpath(
            '//h1[@class="content_left_title"]/text()'
            '|//h1[@class="content_left_title"]/a/text()'
            '|//div[@class="content_title"]/div/text()'
            '|//h1[@class="page_title"]/text()'
            '|//h1[@class="content_left_title"]/p/a/text()'
        ).extract_first(default="").strip()
        # title = response.xpath('//div[@class="content_title"]/div/text()|//h1[@class="page_title"]/text()').extract_first(default="").strip()
        # 特殊情况修正
        if not title:
            title = response.xpath('//meta[@name="keywords"]/@content').extract_first(default="").strip()
        try:
            if not title:
                title = re.search(r"\">(.+?)<", response.xpath('//input[@id="newstitle"]/@value').extract_first(default="")).groups()[0].strip()
        except:
            pass
        if not title:
            title = response.xpath('//title/text()').extract_first(default="").strip()

        return title

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
        time_ = r"".join(response.xpath('//div[@class="content_left_time"]/text()').extract())
        if time_:
            if "来源" in time_:
                time_ = time_.split("来源：")[0]
            return str(datetime.datetime.strptime(time_.strip(), "%Y年%m月%d日 %H:%M"))
        else:
            time_ = r"".join(response.xpath('//div[@class="left"]/p/text()').extract())
            if time_:
                if "来源" in time_:
                    time_ = time_.split("来源：")[0].replace("发布时间：", "")
                return str(datetime.datetime.strptime(time_.strip(), "%Y年%m月%d日 %H:%M"))

            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        video_url = re.findall('source:"(.*.mp4)', response.text)
        if video_url:
            video_dic = {
                "type": "video",
                "src": video_url[0],
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_url[0]) + ".mp4"
            }
            content.append(video_dic)

        news_tags = response.xpath('//div[@class="left_zw"]/*|'
                                   '//div[@class="content_desc"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "video":
                    video_dict = self.parse_media(response, news_tag, media_type="mp4")
                    if video_dict:
                        content.append(video_dict)

                if news_tag.root.tag == "div":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        # 提取视频
        try:
            video_url = re.search(r'\"vInfo\",.+?\"(.+?)\"', response.text).groups()[0]
            suffix = video_url.split(".")[-1].lower()
            if suffix == "mp4":
                content.append({
                    "type": "video",
                    "src": video_url,
                    "name": None,
                    "description": None,
                    "md5src": self.get_md5_value(video_url) + f'.{suffix}'
                })
        except:
            pass

        # 特殊情况处理：-> https://www.chinanews.com.cn/tp/hd2011/2023/01-13/1056526.shtml
        try:
            # 提取图像
            for img in re.findall(r'\<image\>\<\!\[CDATA\[(.+?)\]', response.text):
                suffix = img.split(".")[-1].lower()
                content.append({
                    "type": "image",
                    "name": None,
                    "md5src": self.get_md5_value(img) + f'.{suffix}',
                    "description": "",
                    "src": img
                })
            # 提取描述
            for text in response.xpath('//div[@class="left desc"]/p/text()').extract():
                text = text.strip()
                text and content.append({"data": text, "type": "text"})
        except:
            import traceback
            print(traceback.format_exc())
            pass

        # 特殊情况处理: 外链
        outside_link = response.xpath('//div[@class="left_zw"]/a/text()').extract_first(default="").strip()
        outside_link and content.append({
            "data": outside_link,
            "type": "text"
        })

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        dic = {}
        if cons:
            if new_cons:
                dic['data'] = "".join(cons).strip()
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
            if img.startswith("data:image/gif;base64"):
                return {}
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
