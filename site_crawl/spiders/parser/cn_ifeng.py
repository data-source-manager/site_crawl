# Name: (凤凰网)站点解析器开发
# Date: 2023-02-14
# Author: liyun
# Desc: None
import json
import re
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class CnIfengParser(BaseParser):
    name = 'ifeng'
    
    # 站点id
    site_id = "d02d5035-1989-4b78-b7c9-39537bc00c7d"
    # 站点名
    site_name = "凤凰网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "d02d5035-1989-4b78-b7c9-39537bc00c7d", "source_name": "凤凰网", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f05ba088-2d77-47ce-b02d-b6740ea0b011", "与世界对话", "https://news.ifeng.com/c/special/81iPSl49iNc", "政治"),
            ("4664457b-812b-47d2-9f18-441b6c01d811", "主页", "https://news.ifeng.com/c/special/81iPSl49iNc", "政治"),
            ("15a8ccb5-4100-479b-8766-2f7fc3041b8a", "军事", "https://mil.ifeng.com/", "军事"),
            ("63a19403-1748-425f-9bf2-6e2b2b230dff", "军事/军事社区", "https://help.ifeng.com/index.html?page=1", "军事"),
            ("a654fb28-a3cc-40f1-8248-32437fc19725", "军事/军情热点", "https://mil.ifeng.com/shanklist/14-35083-", "军事"),
            ("5af67fec-1ccd-4664-a49f-3572a55fa086", "军事/军机处", "https://mil.ifeng.com/c/special/7wlNUdim0J6", "军事"),
            ("440aca21-cb06-4981-8e3a-783f1bccc0a3", "军事/战争历史", "https://mil.ifeng.com/shanklist/14-35086-", "军事"),
            ("c11e4c5b-5a38-4d0a-ba05-f2f8213f66b7", "政务", "https://gov.ifeng.com/", "政治"),
            ("a10025a5-2325-4953-a428-ab2d7056a5c9", "政务/人事", "https://gov.ifeng.com/shanklist/22-35144-", "政治"),
            ("61a5572b-9842-4ce8-9d3d-7a518a30d726", "政务/政策", "https://gov.ifeng.com/shanklist/22-35143-", "政治"),
            ("7977e03d-77e2-4c44-a0bc-77220805ddf3", "政务/要闻", "https://gov.ifeng.com/shanklist/22-35141-", "政治"),
            ("8d16d2cc-ff03-46f2-aba5-254f26f97ae5", "政务/高层动态", "https://gov.ifeng.com/shanklist/22-35142-", "政治"),
            ("7155a947-e057-4435-be47-5de4c422a77c", "风向", "https://news.ifeng.com/shanklist/3-245389-/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//h2/a/@href'
            '|//p[@class="text-2le1d12G"]/a/@href'
        ).extract() or []
        try:
            datas = json.loads(re.search(r'var allData = (.+?);\n', response.text).groups()[0])
            news_urls = news_urls or [url["url"] for url in datas.get("newsstream", []) if url.get("url")]
        except:
            pass
        for news_url in list(set(news_urls)):
            url = urljoin(response.url, news_url)
            if "news.ifeng.com" in url:
                yield url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//meta[@name="DC.Publisher"]/@content').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//meta[@name="og:time "]/@content').extract_first()
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(datetime_helper.fuzzy_parse_timestamp(_time))))
        except:
            return "9999-01-01 00:00:00"
        # try:
        #     _time = response.xpath('//div[@id="main-column"]/p[1]/strong/text()').extract_first()
        #     m, d, y = _time.strip().split(" ")
        #     def transf_month(m):
        #         months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        #         return {months[i]:(f'0{i+1}' if i+1<10 else f'{i+1}') for i in range(len(months))}.get(m)
        #     return f"{y}-{transf_month(m)}-{d.strip(',')} 00:00:00"
        # except:
        #     return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return [a.strip() for a in
                response.xpath('//meta[@name="keywords"]/@content').extract_first(default="").split(" ") or []]

    def get_content_media(self, response) -> list:
        content = []
        # 解析视频
        try:
            video_src = ""
            if response.url.startswith("https://v.ifeng.com/"):
                video_src = response.xpath('//meta[@name="og:img_video"]/@content').extract_first(default="").strip()
            else:
                datas = json.loads(re.search(r'var allData = (.+?);\n', response.text).groups()[0])
                video_src = datas["docData"]["contentData"]["contentList"][0]["data"]["playUrl"]
            suffix = video_src.split(".")[-1].lower()
            if suffix in ["mp4"]:
                content.append({
                    "type": "video",
                    "src": video_src,
                    "name": "",
                    "md5src": self.get_md5_value(video_src) + f'.{suffix}',
                    "description": "",
                })
        except:
            pass
        # 解析正文数据
        for tag in response.xpath(
                '//div[@class="text-3w2e3DBc"]/*'
                '|//div[@class="text-3w2e3DBc"]//img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                # 正文结束标记
                if text in ["特别鸣谢"]:
                    break
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
            # 解析图像数据
            elif tag.root.tag == "img":
                img_src = tag.attrib.get("data-lazyload", "")
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
        return "cn"

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
