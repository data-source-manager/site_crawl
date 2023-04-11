# -*- coding: utf-8 -*-
# update:(liyun|2023-01-30) -> 新增板块与解析代码
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal.datetime_helper import parseTimeWithOutTimeZone
from util.tools import check_img


class UsaCnasParser(BaseParser):
    name = 'cnas'
    
    # 站点id
    site_id = "aa90263c-6ed4-4375-a397-1f49127a4700"
    # 站点名
    site_name = "新美国安全中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "aa90263c-6ed4-4375-a397-1f49127a4700", "source_name": "新美国安全中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4b26c665-0f98-4e98-969f-4255a846e597", "军事、退伍军人与社会", "https://www.cnas.org/research/military-veterans-and-society", "军事"),
            ("03748ee5-a505-4967-9ae1-f25e9ba379bf", "军事、退伍军人与社会/军事", "https://www.cnas.org/military", "军事"),
            ("4c9fe639-6b22-4bcd-8cd4-4fa8971f76bf", "印太安全", "https://www.cnas.org/research/indo-pacific-security", "军事"),
            ("5cc94eeb-fae0-464f-bedc-838ae186a908", "印太安全/中国挑战", "https://www.cnas.org/research/indo-pacific-security/china", "军事"),
            ("77619221-e19a-4f55-969c-6cde48a28dec", "国防", "https://www.cnas.org/research/defense", "军事"),
            ("7044312b-651b-40c6-8dc3-a3d8c03dbf72", "国防/加强威慑", "https://www.cnas.org/research/defense/strengthening-deterrence", "军事"),
            ("24a0ea43-2520-4522-a412-2fa772307a7a", "国防/国防的艰难选择", "https://www.cnas.org/research/defense/hard-choices-in-defense", "军事"),
            ("dda04ed2-f65d-4607-82ea-15243dc82e5d", "国防/国防讨论", "https://www.cnas.org/research/defense/defense-discussions", "军事"),
            ("4089dfd3-6aa2-4790-a7f4-8685d61a9360", "国防/战争的未来", "https://www.cnas.org/research/defense/the-future-of-warfare", "军事"),
            ("759d9c4c-c7c5-491c-bf50-5113fa402721", "能源、经济与安全", "https://www.cnas.org/research/energy-economics-and-security", "经济"),
            ("de69f03a-e5ae-4dc8-b018-bb6af2fd9899", "能源、经济与安全/有针对性的制裁：俄罗斯和伊朗", "https://www.cnas.org/research/energy-economics-and-security/sanctions", "经济"),
            ("1c27d427-8e56-4708-834a-280ebd54f470", "能源、经济与安全/经济治国方略", "https://www.cnas.org/research/energy-economics-and-security/economic-statecraft", "经济"),
            ("4ecc5ee3-ae8d-49b5-9b5b-d4e18b81abe0", "跨大西洋安全", "https://www.cnas.org/research/transatlantic-security", "军事"),
            ("31e1ef39-0b2b-42e2-bb81-db383b21a527", "跨大西洋安全/俄罗斯", "https://www.cnas.org/research/transatlantic-security/russia", "政治"),
            ("f76bc0e0-2d9d-40e3-aaa5-c092c1befaac", "跨大西洋安全/直面民族威胁", "https://www.cnas.org/research/transatlantic-security/confronting-threats-to-democracy", "社会"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "aa90263c-6ed4-4375-a397-1f49127a4700"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="labeled-image"]/a/@href'
        ).extract() or []
        for news_url in news_urls:
            news_url = urljoin(response.url, news_url)
            if len(news_url.split('/')) == 4 and news_url != 'https://www.cnas.org/military':
                continue
            yield news_url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        authors = response.xpath('//a[@class="contributor"]/text()').extract() or []
        return [a.strip() for a in authors]

    def get_pub_time(self, response) -> str:
        # February 27, 2023
        time_ = response.xpath('//div[@class="attribution-block"]/p[contains(@class,"uppercase")]/text()').extract_first()
        if time_:
            time_ = datetime.strptime(time_, "%B %d, %Y")
            return parseTimeWithOutTimeZone(time_, site_name="新美国安全中心")

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        news_tags = response.xpath(
            '//div[@id="mainbar"]/div/*'
            '|//div[@id="mainbar"]//p'
            '|//figure[@class="hero"]/picture/source'
            '|//div[@id="mainbar-toc"]/div/*'
            '|//div[@id="mainbar-toc"]//img'
            '|//main[@id="content"]/article/div/*'
            '|//main[@id="content"]/article/header//img'
            '|//figure[@class="margin-vertical "]/div/iframe'
            '|//div[@class="embed margin-vertical "]//iframe'
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
            elif tag.root.tag in ["img", "source"]:
                img_src = tag.attrib.get("srcset", "").split("?")[0] or tag.attrib.get("src", "").split("?")[0]
                if not img_src.startswith('http'):
                    continue
                suffix = img_src.split(".")[-1].lower()
                img_src and content.append({
                    "type": "image",
                    "name": tag.attrib.get('title', "").strip(),
                    "md5src": self.get_md5_value(img_src) + f'.{suffix}',
                    "description": tag.attrib.get('alt', "").strip(),
                    "src": img_src
                })
            # 解析媒体资源
            elif tag.root.tag == "iframe":
                media_url = tag.attrib.get("src")
                if not media_url:
                    continue
                media_url = media_url if media_url.startswith("https:") else f'https:{media_url}'
                media_type = "video" if media_url.startswith("https://www.youtube.com/") else "audio"
                content.append({
                    "type": media_type,
                    "src": media_url,
                    "name": None,
                    "description": None,
                    "md5src": self.get_md5_value(media_url) + (".mp4" if media_type == "video" else ".mp3")
                })
            else:
                pass
        # 解析PDF资源
        for tag in response.xpath(
                '//div[@class="download-callout"]//a'
                '|//div[@id="mainbar"]/div/center/h3/em/a'
        ):
            url = tag.attrib.get("href", "").split("?")[0].strip()
            suffix = url.split(".")[-1].lower()
            if suffix in ["pdf"]:
                content.append({
                    "type": "file",
                    "src": url,
                    "name": tag.attrib.get('title'),
                    "description": None,
                    "md5src": self.get_md5_value(url) + f".{suffix}"
                })

        # img_list = response.xpath('//meta[@property="og:image"]/@content')
        # if img_list:
        #     for img in img_list:
        #         header_img = self.parse_img(response, img)
        #         if header_img:
        #             content.append(header_img)

        # news_tags = response.xpath('//div[contains(@id,"mainbar")]/div/*')
        # if news_tags:
        #     for news_tag in news_tags:
        #         if news_tag.root.tag in ["h2", "h3","h4" "h5", "span", "p", "div"]:
        #             if news_tag.root.tag == "div":
        #                 video = news_tag.xpath('.//div[@class="media-16x9"]/iframe/@src').extract()
        #                 if video:
        #                     if not video.startswith("http"):
        #                         video = "https:" + video
        #                     video_dic = {
        #                         "type": "video",
        #                         "src": video,
        #                         "name": None,
        #                         "description": None,
        #                         "md5src": self.get_md5_value(video) + ".mp4"
        #                     }
        #                     content.append(video_dic)
        #                 file = news_tag.xpath('.//p/a[contains(@href,"pdf")]/@href').extract()
        #                 if file:
        #                     con_file = self.parse_file(response, news_tag.xpath(".//p/a"))
        #                     if con_file:
        #                         content.append(con_file)
        #             text_dict = self.parseOnetext(news_tag)
        #             if text_dict:
        #                 content.extend(text_dict)
        # video = response.xpath('//div[@class="media-16x9"]/iframe/@src').extract_first()
        # if video:
        #     if not video.startswith("http"):
        #         video = "https:" + video
        #     video_dic = {
        #         "type": "video",
        #         "src": video,
        #         "name": None,
        #         "description": None,
        #         "md5src": self.get_md5_value(video) + ".mp4"
        #     }
        #     content.append(video_dic)
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
                if "Download" in x.strip():
                    return []
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
        img = news_tag.xpath('./@content').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.attrib.get('alt'),
                   "src": img_url
                   }
            return dic

    def parse_single_img(self, response, news_tag):
        img_list = []

        img_src = news_tag.xpath("./@src").extract_first()
        if check_img(img_src):
            img_url = urljoin(response.url, img_src)
            des = "".join(news_tag.xpath('.//figcaption//text()').extract()).strip()
            if not des:
                des = "".join(news_tag.xpath(".//@alt").extract())

            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', ""),
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

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("").extract_first()
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
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
