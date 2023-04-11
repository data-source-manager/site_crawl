# -*- coding: utf-8 -*-
# update:(liyun|2023-03-15) -> 板块核对与解析代码修正
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TW_taiwandailyParser(BaseParser):
    '''
    存在评论
    '''
    name = 'tw_taiwandaily'
    # 站点id
    site_id = "0db855ee-9a0c-43fd-8b43-614ee727f8b0"
    # 站点名
    site_name = "美洲台湾日报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "0db855ee-9a0c-43fd-8b43-614ee727f8b0", "source_name": "美洲台湾日报", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8ea296-fe6f-11ec-a30b-d4619d029786", "专栏", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/", "政治"),
            ("805383ea-e17a-4aa4-94e6-89e902c7c47b", "专栏/BECKON", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/beckon/", "政治"),
            ("cf5c328a-c8d2-4467-be0c-98294f28c8f4", "专栏/公孙乐", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/%e5%85%ac%e5%ad%ab%e6%a8%82/", "政治"),
            ("f71e9794-d5fa-495e-9818-3047fc92c914", "专栏/兰雨静", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/%e8%98%ad%e9%9b%a8%e9%9d%9c/", "政治"),
            ("6cbdccda-0483-4b0a-8fd7-24d2d37e2bce", "专栏/外国伦", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/%e5%a4%96%e5%9c%8b%e5%80%ab/", "政治"),
            ("9265dc9d-70af-467d-8512-6e058ffaf8c8", "专栏/徐惠", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/%e5%be%90%e6%83%a0/", "政治"),
            ("fe5e7a48-a040-4d1f-a59b-94d50b8c6c25", "专栏/林莲华", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/%e6%9e%97%e8%93%ae%e8%8f%af/", "政治"),
            ("4674387a-53e1-4b57-90e9-4c537ab9da93", "专栏/英夫", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/%e8%8b%b1%e5%a4%ab/", "政治"),
            ("ef4f8fcd-e4cc-4615-a38f-a77f2e0f883a", "专栏/陈文石", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/%e9%99%b3%e6%96%87%e7%9f%b3/", "政治"),
            ("8c0e69e2-c9d7-4028-9519-b78b24ff8c2e", "专栏/霸谷", "https://www.taiwandaily.net/category/%e5%b0%88%e6%ac%84/%e9%9c%b8%e8%b0%b7/", "政治"),
            ("4a8ea2c8-fe6f-11ec-a30b-d4619d029786", "台美人物", "https://www.taiwandaily.net/category/%e5%8f%b0%e7%be%8e%e4%ba%ba%e7%89%a9/", "政治"),
            ("d6dbb86d-29f7-4e44-a82d-85df2ebb6aa1", "影音", "https://www.taiwandaily.net/category/new-look-2015/", "政治"),
            ("2287f47b-65bb-4b3c-9622-45dafba09f90", "影音/政论影音", "https://www.taiwandaily.net/category/new-look-2015/fashion/", "政治"),
            ("50733e07-ccc8-4c77-8f83-1d812cbcb48f", "影音/新闻影音", "https://www.taiwandaily.net/category/new-look-2015/street-fashion/", "政治"),
            ("4a8ea264-fe6f-11ec-a30b-d4619d029786", "政治评论", "https://www.taiwandaily.net/category/%e6%94%bf%e6%b2%bb%e8%a9%95%e8%ab%96/", "政治"),
            ("9c79c819-9662-42b8-b024-d2259acc735f", "新闻", "https://www.taiwandaily.net/category/%e5%8d%b3%e6%99%82%e6%96%b0%e8%81%9e/", "政治"),
            ("4a8ea1a6-fe6f-11ec-a30b-d4619d029786", "新闻/台湾新闻", "https://www.taiwandaily.net/category/%e5%8d%b3%e6%99%82%e6%96%b0%e8%81%9e/%e5%8f%b0%e7%81%a3%e6%96%b0%e8%81%9e/", "政治"),
            ("4a8ea232-fe6f-11ec-a30b-d4619d029786", "新闻/国际新闻", "https://www.taiwandaily.net/category/%e5%8d%b3%e6%99%82%e6%96%b0%e8%81%9e/%e5%9c%8b%e9%9a%9b%e6%96%b0%e8%81%9e/", "政治"),
            ("4a8ea1f6-fe6f-11ec-a30b-d4619d029786", "新闻/美国新闻", "https://www.taiwandaily.net/category/%e5%8d%b3%e6%99%82%e6%96%b0%e8%81%9e/%e5%9c%8b%e9%9a%9b%e6%96%b0%e8%81%9e/", "政治"),
            ("e4d8e698-35ee-4996-99dc-c70b6c654d0b", "评论", "https://www.taiwandaily.net/category/%e6%94%bf%e6%b2%bb%e8%a9%95%e8%ab%96/", "政治"),
            ("c14e8318-3425-41eb-92db-8eef15628029", "评论/台湾政论", "https://www.taiwandaily.net/category/%e6%94%bf%e6%b2%bb%e8%a9%95%e8%ab%96/%e5%8f%b0%e7%81%a3%e6%94%bf%e8%ab%96/", "政治"),
            ("bbdb69c6-e52e-4ae7-b56d-560baa6a0fc5", "评论/海外观点", "https://www.taiwandaily.net/category/%e6%94%bf%e6%b2%bb%e8%a9%95%e8%ab%96/%e6%b5%b7%e5%a4%96%e8%a7%80%e9%bb%9e/", "政治"),
            ("cb54d0ac-0efa-4247-b678-3e924a6d0f0f", "评论/社论", "https://www.taiwandaily.net/category/%e6%94%bf%e6%b2%bb%e8%a9%95%e8%ab%96/%e7%a4%be%e8%ab%96/", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="td-ss-main-content"]//h3/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//h1[@class="entry-title"]/text()').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//div[@class="td-post-author-name"]/a/text()').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//time[@class="entry-date updated td-module-date"]/@datetime').extract_first(default="").strip()
            publish_date = datetime_helper.parseTimeWithTimeZone(publish_date)
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="td-post-content"]/*'
            '|//div[@class="td-post-content"]//img'
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
        # 解析视频
        try:
            video_src = response.xpath('//div[@class="rll-youtube-player"]/@data-id').extract_first(default="").strip()
            if video_src:
                video_src = f"https://www.youtube.com/watch?v={video_src}"
                content.append({
                    "type": "video",
                    "src": video_src,
                    "name": None,
                    "description": None,
                    "md5src": self.get_md5_value(video_src) + ".mp4"
                })
        except:
            pass
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def get_like_count(self, response) -> int:
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        read_count_str = response.xpath("//span[contains(@class,'views post-meta-views')]/text()").get()
        if read_count_str:
            read_count = int(read_count_str.replace(",", ""))
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
