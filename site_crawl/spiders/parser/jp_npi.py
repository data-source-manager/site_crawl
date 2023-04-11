# -*- coding: utf-8 -*-
# update:(liyun|2023-01-31) -> 板块核对与解析代码修正
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class JP_npiParser(BaseParser):
    name = 'jp_npi'
    
    # 站点id
    site_id = "dd3bd6d0-6975-49be-817b-265eee0e3a7c"
    # 站点名
    site_name = "世界和平研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "dd3bd6d0-6975-49be-817b-265eee0e3a7c", "source_name": "世界和平研究所", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("8c104d39-268c-48c9-bac2-83d6be3b9ec1", "外交和安全", "https://npi.or.jp/research/diplomacy/index.html", "政治"),
            ("b74dd73d-5b73-4ded-bb0a-249a4929dd79", "宪政", "https://npi.or.jp/research/government/index.html", "政治"),
            ("835d47ee-486b-4375-8534-58e6b7298120", "政策建议", "https://npi.or.jp/research/policy/index.html", "政治"),
            ("fafae96c-45b1-439b-95db-91c2bcf558f5", "经济和社会", "https://npi.or.jp/research/economy/index.html", "经济"),
            ("46ac487b-6402-4e1a-b060-5c5e5a97961a", "经济安全", "https://npi.or.jp/research/industry/index.html", "经济"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "dd3bd6d0-6975-49be-817b-265eee0e3a7c"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="box"]/p/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("|")[0].strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//h3[@class="ttl_second b30"]/div/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        # 解析正文数据
        news_tags = response.xpath(
            '//div[@class="detail_area"]/div/*'
            '|//div[@class="detail_area"]//img'
            '|//div[@class="t30 flex jc_c"]//a'
            '|//div[@class="detail_area"]//a'
        ) or []
        for tag in news_tags:
            # 解析文本数据
            if tag.root.tag in ["p", "h2", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text and content.append({"data": text, "type": "text"})
            # 解析图像数据
            elif tag.root.tag in ["img"]:
                img_src = tag.attrib.get("src", "").split("?")[0]
                suffix = img_src.split(".")[-1].lower()
                if not img_src.startswith('http') and suffix not in ['jpg', 'png', 'jpeg']:
                    continue
                img_src = urljoin(response.url, img_src)
                img_src and content.append({
                    "type": "image",
                    "name": tag.attrib.get('title', "").strip(),
                    "md5src": self.get_md5_value(img_src) + f'.{suffix}',
                    "description": tag.attrib.get('alt', "").strip(),
                    "src": img_src
                })
            # 解析PDF资源
            elif tag.root.tag == "a":
                file_src = urljoin(response.url, tag.attrib.get("href"))
                if not file_src.endswith("pdf"):
                    continue
                content.append({
                    "type": "file",
                    "src": file_src,
                    "name": tag.attrib.get('title'),
                    "description": None,
                    "md5src": self.get_md5_value(file_src) + ".pdf"
                })
            else:
                pass

        # news_tags = response.xpath('//div[@class="b0"]/p|//div[@class="detail_img_area"]/a|'
        #                            '//div[@class="t30 flex jc_c"]/a')
        # if news_tags:
        #     for news_tag in news_tags:
        #         if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
        #             text_dict = self.parseOnetext(news_tag)
        #             if text_dict:
        #                 content.extend(text_dict)
        #         if news_tag.root.tag == "ul":
        #             for con in news_tag.xpath('./li'):
        #                 con_text = self.parseOnetext(con)
        #                 if con_text:
        #                     content.extend(con_text)
        #         if news_tag.root.tag == "a":
        #             con_file = self.parse_file(response, news_tag)
        #             if con_file:
        #                 content.append(con_file)

        #         if news_tag.root.tag == "a":
        #             con_img = self.parse_img(response, news_tag)
        #             if con_img:
        #                 content.extend(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('').extract() or ""

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
