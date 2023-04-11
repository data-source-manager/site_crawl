# update:(liyun:2023-03-07) -> 新增板块与解析代码覆盖
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


class JpMainichiParser(BaseParser):
    name = 'mainichi'

    
    # 站点id
    site_id = "c23facc4-1467-42ee-832a-aad4f4ecc571"
    # 站点名
    site_name = "日本每日新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "c23facc4-1467-42ee-832a-aad4f4ecc571", "source_name": "日本每日新闻", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("cb0bcab3-4fe5-4042-a868-a301f42c1e4a", "国际", "https://mainichi.jp/world/", "其他"),
            ("ed4991a4-e30a-45de-b686-6daaac6f055e", "意见", "https://mainichi.jp/opinion/", "其他"),
            ("1c9cb889-73c3-4d6c-9021-57783671617e", "政治", "https://mainichi.jp/seiji/", "政治"),
            ("c8b82316-f795-48a7-816a-4a5c15c820a0", "文化", "https://mainichi.jp/culture/", "其他"),
            ("4a8f8d96-fe6f-11ec-a30b-d4619d029786", "毎日新闻", "https://mainichi.jp/information/0?&_=1642583507881", "政治"),
            ("5b1f7970-0539-451b-98dc-121eb202ca1e", "环境与科学", "https://mainichi.jp/science/", "其他"),
            ("849cddc0-0acf-418b-b5e5-f23e38963901", "生活、学习和医疗", "https://mainichi.jp/life/", "其他"),
            ("d95e45ac-02b6-4456-8249-760ffc9a8da4", "社会", "https://mainichi.jp/shakai/", "社会"),
            ("cb0bcab5-4fe5-4042-a868-a301f42c1e4a", "经济", "https://mainichi.jp/biz/", "经济"),
            ("c6cff570-a3c2-464a-8944-27662e81fae5", "速报", "https://mainichi.jp/flash/", "社会"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//ul[@class="articlelist is-tophorizontal js-morelist"]//li/a/@href'
            '|//div[@class="categorypickup"]/a/@href'
            '|//ul[@class="articlelist"]/li/a/@href'
            '|//ul[@class="articlelist js-morelist"]/li/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@name="title"]/@content').extract_first(default="").split("|")[0].strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        try:
            pub_time = response.xpath('//meta[@name="firstcreate"]/@content').extract_first(default="")
            pub_time = datetime.strptime(pub_time.strip(), "%Y-%m-%d %H:%M:%S")
            pub_time = datetime_helper.parseTimeWithOutTimeZone(pub_time, site_name="日本每日新闻")
            return pub_time
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//section[@id="articledetail-body"]/*'
            '|//div[@class="main-column"]/*'
            '|//div[@class="main-column"]//img'
            '|//section[@id="articledetail-body"]//img'
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
     
        # news_tags = response.xpath('//section[@id="articledetail-body"]/*'
        #                            '|//section[@id="articledetail-body"]//img') or []
        # for news_tag in news_tags:
        #     if news_tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
        #         text_dict = self.parseOnetext(news_tag)
        #         if text_dict:
        #             content.extend(text_dict)
        #     if news_tag.root.tag == "ul":
        #         for con in news_tag.xpath('./li'):
        #             con_text = self.parseOnetext(con)
        #             if con_text:
        #                 content.extend(con_text)
        #     if news_tag.root.tag == "img":
        #         con_img = self.parse_single_img(response, news_tag)
        #         if con_img:
        #             content.extend(con_img)
        

    def get_detected_lang(self, response) -> str:
        return "ja"

    def parse_text(self, news_tag):
        cons = news_tag.xpath('.//text()').extract() or ""

        new_cons = []

        if cons:
            for con in cons:
                if con.strip():
                    new_cons.append({'data': "".join(con).strip(), 'type': "text"})
        return new_cons

    def parseOnetext(self, news_tag) -> list:
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

    def parse_many_img(self, response, news_tag):
        imgs = news_tag.xpath('.//img')

        img_list = []

        if imgs:
            for img in imgs:
                img_src = img.xpath("./@src").extract_first()
                if check_img(img_src):
                    img_url = urljoin(response.url, img_src)

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
