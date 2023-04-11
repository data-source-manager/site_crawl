# -*- coding: utf-8 -*-
# update:(liyun|2023-01-07) -> 正文数据异常换行问题修正
# update:(liyun|2023-01-31) -> 板块核对与修正

import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwNpfParser(BaseParser):
    name = 'npf'
    
    # 站点id
    site_id = "e0462ecb-1ca9-4c40-975b-dfcdc85cf11b"
    # 站点名
    site_name = "财团法人国家政策研究基金会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e0462ecb-1ca9-4c40-975b-dfcdc85cf11b", "source_name": "财团法人国家政策研究基金会", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4ac2fab8-9fbe-6364-07a5-733ff32c9a2e", "最新文章", "", "政治"),
            ("395d5f07-ebb5-47cd-81b0-34a02e4ce846", "最新文章/国政分析", "https://www.npf.org.tw/categories/3", "政治"),
            ("8ab23326-2dd1-4e44-af10-ef21e7bb04c7", "最新文章/国政研究", "https://www.npf.org.tw/categories/2", "政治"),
            ("e0af6e68-9d0d-4527-a883-8034bf59d5d7", "最新文章/国政评论", "https://www.npf.org.tw/categories/1", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "e0462ecb-1ca9-4c40-975b-dfcdc85cf11b"
        self.pub = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@id="listarticleright"]/p/a')
        if news_urls:
            for news_url in news_urls:
                url = urljoin(response.url, news_url.xpath("./@href").extract_first())
                pub = news_url.xpath("./span[@class='timetag']/span/span/@title").extract_first()
                self.pub[url] = pub
                yield url

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="dable:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@property="dable:author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = self.pub[response.url]
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@style="float:left;"]/a/span/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    """
    @fix: liyun - 2023-01-07: 正文数据异常换行问题修正
    @TODO: 正文数据中的表格解析异常，确定修复方案后修正 
    """

    def get_content_media(self, response) -> list:
        content = []

        # 解析图像数据
        img_duplicate_set = set()
        for img in response.xpath('//img[@class="rwdimg"]'):
            img_url = urljoin(response.url, img.attrib.get("src"))
            if (img_url.split(".")[-1].lower() not in ["jpg", "png"]) or (img_url in img_duplicate_set):
                continue
            content.append({
                "type": "image",
                "name": img.attrib.get('title', None),
                "md5src": self.get_md5_value(img_url) + '.jpg',
                "description": img.attrib.get('alt', "").strip(),
                "src": img_url
            })
            img_duplicate_set.add(img_url)
        # 解析正文数据
        p_text = ""
        for text in response.xpath('//div[@id="articlebody"]//text()').extract():
            text = text.strip()
            p_text += text
            if not text:
                p_text and content.append({"data": p_text, "type": "text"})
                p_text = ""
        else:
            p_text and content.append({"data": p_text, "type": "text"})

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
