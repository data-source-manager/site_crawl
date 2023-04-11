# -*- coding: utf-8 -*-
from urllib.parse import urljoin

import langdetect

from .base_parser import BaseParser


class KcfrParser(BaseParser):
    name = 'kcfr'
    
    # 站点id
    site_id = "c1448c3c-1afa-48a9-9a51-ad3f0196f5ac"
    # 站点名
    site_name = "韩国对外关系协会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c1448c3c-1afa-48a9-9a51-ad3f0196f5ac", "source_name": "韩国对外关系协会", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("91233c06-2f72-11ed-a768-d4619d029786", "外交广场", "https://www.kcfr.or.kr/bbs/board.php?bo_table=612", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        urls = response.xpath('//div[@class="bo_tit"]/a/@href').extract()
        if urls:
            for url in urls:
                yield urljoin(response.url, url)
                # yield "https://jacksonville.tricare.mil/News-Gallery/Articles/Article/3028304/patients-at-naval-branch-health-clinic-kings-bay-can-take-steps-now-to-prepare/"

    def get_title(self, response) -> str:
        title = response.xpath('//span[@class="bo_v_tit"]/text()').extract_first(default="")
        return title.strip() or ""

    def get_author(self, response) -> list:
        author = response.xpath('//p[@class="info"]/span[1]/text()').extract_first()
        if author:
            author = author.replace("By", "").strip()
            return [author]
        return []

    def get_pub_time(self, response) -> str:
        # 2022-01-21T03:21:00.2100000
        pub = response.xpath('//strong[@class="if_date"]/text()').extract_first()
        if pub:
            return pub.strip()
        else:
            pub_time = "9999-01-01 00:00:00"
        return pub_time

    def get_tags(self, response) -> list:
        tag_list = []
        tags = response.xpath('//div[@class="tags"]//a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tag_list.append(tag.strip())
        return tag_list

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@id="bo_v_con"]/p'
        )
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "li"]:
                    if news_tag.xpath('.//img/@src').extract_first():
                        content.append(self.parse_img(response, news_tag))
                    text_dict = self.parse_text(news_tag)
                    content.extend(text_dict)

        file = response.xpath('//section[@id="bo_v_file"]//a')
        if file:
            file_src = urljoin(response.url, file.xpath('./@href').extract_first())
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": "".join(file.xpath(".//text()").extract()).strip(),
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            content.append(file_dic)
        return content

    def get_detected_lang(self, response) -> str:
        title = self.get_title(response)
        if title:
            return langdetect.detect(f"{title}")
        else:
            print('error, no title url:' + response.url)
            return ''

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                dic = {}
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        img = news_tag.xpath(".//img/@src").extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.xpath(".//img/@lt").extract_first(),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": None,
                   "src": img_url
                   }
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath(".//a/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath(".//a/text()").extract_first(),
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url, news_tag.xpath("").extract_first())
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
