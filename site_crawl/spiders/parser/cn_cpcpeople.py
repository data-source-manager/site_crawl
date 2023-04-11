# -*- coding: utf-8 -*-
# update:(liyun|2023-02-13) -> 板块核对与解析代码修正
# update:(liyun|2023-03-08) -> 板块核对与解析代码修正
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class CN_cpcpeopleParser(BaseParser):
    name = 'cn_cpcpeople'
    
    # 站点id
    site_id = "4abf8582-0865-408b-95f4-d481ed306e02"
    # 站点名
    site_name = "人民网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "4abf8582-0865-408b-95f4-d481ed306e02", "source_name": "人民网", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e85dcb3a-92c5-44af-a0bb-bb6bc7114dc3", "中央文件", "http://cpc.people.com.cn/GB/67481/431391/index.html", "政治"),
            ("4a8cd2ea-fe6f-11ec-a30b-d4619d029786", "习近平讲话", "http://jhsjk.people.cn/", "政治"),
            ("b0c21d00-7218-11ed-a54c-d4619d029786", "望海楼", "http://world.people.com.cn/GB/383262/144932/index.html", "政治"),
            ("b0c21c60-7218-11ed-a54c-d4619d029786", "深度报道", "http://world.people.com.cn/GB/14549/index.html", "政治"),
            ("b0c21c06-7218-11ed-a54c-d4619d029786", "滚动新闻", "http://world.people.com.cn/GB/157278/index.html", "政治"),
            ("bba67a3f-000f-42cf-9501-416cbd2b48b3", "要闻", "", "政治"),
            ("2ad74bc5-9e80-4edc-89c0-8d5828bff233", "要闻/军事", "http://military.people.com.cn/", "军事"),
            ("b3d996da-3a09-4e71-abea-752816098f3c", "要闻/台湾", "http://tw.people.com.cn/", "政治"),
            ("25abf846-b9d1-4c58-b950-a043ba951ba5", "要闻/国际", "http://world.people.com.cn/", "政治"),
            ("dca91b8f-70d3-4f5f-8b68-0f17a3a24525", "要闻/港澳", "http://hm.people.com.cn/", "政治"),
            ("fad1993f-9b51-4d88-b7cd-3c0310a5fd7c", "要闻/社会 · 法治", "http://society.people.com.cn/", "社会"),
            ("b0c21cb0-7218-11ed-a54c-d4619d029786", "钟声", "http://world.people.com.cn/GB/383262/144400/index.html", "政治"),
            ("f1dede74-4aed-4b1f-b658-2664faa04dc9", "高层动态", "http://cpc.people.com.cn/GB/64093/64094/index.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        url_filter = [
            "http://hm.people.com.cn/"
        ]
        news_urls = response.xpath(
            '//div[@class="fl"]/ul/li/a/@href'
            '|//div[@class="news"]/b/a/@href'
            '|//div[@class="ej_bor"]/ul[@class="list_ej2  mt20"]/li/a/@href'
            '|//div[@class="c_left fl"]/dl//h2/a/@href'
            '|//div[@class="news"]/ul/li/a/@href'
            '|//div[contains(@class, "hdNews")]//a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            if not news_url.endswith("index.html") and news_url not in url_filter:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//h1/text()').extract_first(default="").strip()

    def get_author(self, response) -> list:
        try:
            authors = response.xpath(
                '//div[@class="edit cf"]/text()'
                '|//div[@class="editor clearfix"]/text()'
            ).extract_first(default="").strip()
            authors = re.sub(r"[(责编：)]", "", authors)
            return [a.strip() for a in authors.split("、")]
        except:
            return []
        
        # author_list = []
        # if "c1002" in response.url:
        #     return []
        # else:
        #     author_str = response.xpath("//div[@class='edit']/text()").get()
        #     if author_str:
        #         author_s = author_str.replace("(责编：", "").replace(")", "")
        #         for author_a in author_s.split("、"):
        #             author_list.append(author_a)
        #     return author_list

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//meta[@name="publishdate"]/@content').extract_first(default="")
            if not _time:
                _time = response.xpath('//div[@class="d2txt_1 clearfix"]/text()').extract_first(default="")
                _time = _time.split("：")[-1].strip()
            pub_time = datetime_helper.fuzzy_parse(_time)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        except:
            return "9999-01-01 00:00:00"
        # """
        # 时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        # """
        # time_ = response.xpath("//p[@class='sou']/text()|//meta[@name='publishdate']/@content").get()
        # if time_:
        #     dt_ = time_.replace("来源：", "").strip().replace("年", "-").replace("月", "-").replace("日", " ").replace(
        #         "|", "")
        #     pub_time = datetime_helper.fuzzy_parse_timestamp(dt_)
        #     return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//div[@class="show_text"]/*'
                '|//div[@class="rm_txt_con cf"]/*'
                '|//div[@class="content clear clearfix"]/p'
                '|//div[@class="d2txt_con clearfix"]/*'
                '|//div[@id="p_content"]/*'
                '|//div[@id="picG"]/img'
                '|//div[@id="p_content"]//img'
                '|//div[@class="rm_txt_con cf"]/p/img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
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

    def get_detected_lang(self, response) -> str:
        return "zh"

    def get_like_count(self, response) -> int:
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        return 0

    def get_if_repost(self, response) -> bool:
        if self.Dict.get(response.url):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        repost_source_str = response.xpath("//p[@class='sou']/a/text()").get()
        if repost_source_str:
            self.Dict[response.url] = repost_source_str
            repost_source = repost_source_str
        return repost_source
