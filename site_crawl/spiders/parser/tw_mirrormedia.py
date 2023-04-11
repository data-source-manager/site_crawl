# -*- coding: utf-8 -*-
# update:(liyun|2023-03-08) -> 板块核对与解析代码修正
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwMirrormediaParser(BaseParser):
    name = 'mirrormedia'

    
    # 站点id
    site_id = "5a334f51-f542-4001-9d1b-fd8e1f7781d9"
    # 站点名
    site_name = "镜周刊"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "5a334f51-f542-4001-9d1b-fd8e1f7781d9", "source_name": "镜周刊", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e978b9e8-52d7-4f95-b680-0d81e059ac9b", "国内", "https://www.mirrormedia.mg/category/political", "政治"),
            ("4a8c5d10-fe6f-11ec-a30b-d4619d029786", "国际", "https://www.mirrormedia.mg/section/international", "政治"),
            ("d6361e1c-72c7-33ea-a4fd-96c585784235", "时事", "https://www.mirrormedia.mg/section/news", "政治"),
            ("bcbebf3c-39a2-4993-92b6-a252e72f0598", "时事/国际要闻", "https://www.mirrormedia.mg/category/global", "政治"),
            ("4a8c5d88-fe6f-11ec-a30b-d4619d029786", "时事/焦点", "https://www.mirrormedia.mg/category/news", "政治"),
            ("a115f1a6-178a-4082-8be2-359c940203fd", "时事/社会", "https://www.mirrormedia.mg/category/city-news", "社会"),
            ("65eb71bd-f00a-4682-b52d-3541ee7239ba", "论坛", "https://www.mirrormedia.mg/section/mirrorcolumn", "政治"),
            ("2ea724d7-e775-4099-9d68-13596e99f4c8", "论坛/名家专栏", "https://www.mirrormedia.mg/category/mirrorcolumn", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@class="article"]/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@property="dable:author"]/@content').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
            pub_time = datetime_helper.fuzzy_parse_timestamp(_time)
            return datetime_helper.parseTimeWithTimeZone(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time))))
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@name="news_keywords"]/@content').extract_first("").split(",") or []]

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//article/*'
            '|//article//p[@class="g-story-paragraph"]'
            '|//article/figure//img'
            '|//div[@class="the-cover"]//img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                if text.startswith("更多內容") or text.startswith("更新時間"):
                    break
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
            # 解析图像数据
            elif tag.root.tag == "img":
                img_src = tag.attrib.get("srcset", "") or tag.attrib.get("src", "")
                if not img_src:
                    continue
                img_src = img_src.split("?")[0].split(" ")[0]
                img_src = urljoin(response.url, img_src)
                suffix = img_src.split(".")[-1].lower()
                if (not img_src.startswith('http')) or (suffix not in ["jpg", 'png', 'jpeg']):
                    continue
                content.append({
                    "type": "image",
                    "src": img_src,
                    "name": tag.attrib.get('alt', "").strip(),
                    "md5src": self.get_md5_value(img_src) + f'.{suffix}',
                    "description": tag.xpath("../figcaption/text()").extract_first(default="").strip(),
                })
            else:
                pass
        return content
        # news_tags = response.xpath('//article/*')
        # if news_tags:
        #     for news_tag in news_tags:
        #         if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
        #             if news_tag.root.tag == "div":
        #                 if "story__youtube" == news_tag.xpath('./@class').extract_first():
        #                     con_video = self.parse_media(response, news_tag, "video")
        #                     if con_video:
        #                         content.append(con_video)
        #                 elif "story__brief" != news_tag.xpath('./@class').extract_first():
        #                     continue
        #             text_dict = self.parseOnetext(news_tag)
        #             if text_dict:
        #                 content.extend(text_dict)
        #         if news_tag.root.tag == "ul":
        #             for con in news_tag.xpath('./li'):
        #                 con_text = self.parseOnetext(con)
        #                 if con_text:
        #                     content.extend(con_text)
        #         if news_tag.root.tag == "figure":
        #             con_img = self.parse_img(response, news_tag)
        #             if con_img:
        #                 content.append(con_img)

        # return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

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
