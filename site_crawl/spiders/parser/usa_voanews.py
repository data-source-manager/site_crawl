# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsavoanewsParser(BaseParser):
    name = 'usa_voanews'
    
    # 站点id
    site_id = "413b6cdb-a777-434d-b6b2-f2f3595b2efa"
    # 站点名
    site_name = "美国之音英文版"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "413b6cdb-a777-434d-b6b2-f2f3595b2efa", "source_name": "美国之音英文版", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b2a4e-fe6f-11ec-a30b-d4619d029786", "东亚", "https://www.voanews.com/z/600", "政治"),
            ("4a8b2c60-fe6f-11ec-a30b-d4619d029786", "中东", "https://www.voanews.com/z/598", "政治"),
            ("764056c0-ba36-40f2-a63b-b24a522e0161", "中国", "https://www.voanews.com/p/7753.html", "政治"),
            ("4a8b2968-fe6f-11ec-a30b-d4619d029786", "乌克兰", "https://www.voanews.com/z/4047", "政治"),
            ("cd6c7ab1-9f1c-4c9b-a45c-dabb59c7e9e3", "伊朗", "https://www.voanews.com/p/7752.html", "政治"),
            ("93a9e9a2-17d5-438f-aeb7-0019e1a5bfce", "关于美国", "https://www.voanews.com/p/6978.html", "政治"),
            ("4a8b2bca-fe6f-11ec-a30b-d4619d029786", "南亚和中亚", "https://www.voanews.com/z/5452", "政治"),
            ("04bf2df3-4463-44d9-b026-67c1543121db", "极端主义观察", "https://www.voanews.com/p/6090.html", "政治"),
            ("4a8b2abc-fe6f-11ec-a30b-d4619d029786", "欧洲", "https://www.voanews.com/z/611", "政治"),
            ("d7a0a1ea-7db5-4813-8540-76da430ba46a", "硅谷与科技", "https://www.voanews.com/p/6290.html", "政治"),
            ("8d12a493-4829-4c6b-990d-6ea89e330d4a", "社论", "", "政治"),
            ("8b4f3874-1c71-4ac6-8914-3347734c5781", "社论/中东", "https://editorials.voa.gov/z/3231", "政治"),
            ("612f2556-218d-4762-b2f7-0561c12630e5", "社论/亚洲", "https://editorials.voa.gov/z/3231", "政治"),
            ("2307f6ba-8eb2-4510-a785-fd6f4a44b6fa", "社论/欧洲", "https://editorials.voa.gov/z/3231", "政治"),
            ("5df6533e-bc23-43b6-9f98-c5a0f4e6d0db", "社论/美洲", "https://editorials.voa.gov/z/3230", "政治"),
            ("6582aef7-1987-4258-9439-f3aca3ec38b4", "社论/非洲", "https://editorials.voa.gov/z/3229", "政治"),
            ("cadbcf62-2a70-4ec3-b255-d3984921930c", "移民", "https://www.voanews.com/p/6722.html", "政治"),
            ("5a6db8cd-1325-4643-a439-ae335ae088cf", "经济与商业", "https://www.voanews.com/p/6288.html", "政治"),
            ("4a8b28e6-fe6f-11ec-a30b-d4619d029786", "美国政治", "https://www.voanews.com/z/4720", "政治"),
            ("5093148b-bad9-4dc8-ae61-894eae3de7b2", "美国新闻", "https://www.voanews.com/z/599", "政治"),
            ("d84e3dab-07a7-40f6-a3b2-fcaf79521b66", "美洲", "https://www.voanews.com/p/6210.html", "政治"),
            ("6b83fec4-7db3-4ea1-9fd6-964b73854778", "非洲", "https://www.voanews.com/p/5749.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "413b6cdb-a777-434d-b6b2-f2f3595b2efa"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//div[@class='media-block__content media-block__content--h media-block__content--h-xs']/a/@href|"
            "//div[@class='media-block-wrap']//div[@class='media-block ']/a/@href").extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1/text()|//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//time/@datetime').get()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="photo-container"]/img|'
                                  '//div[@data-u="slides"]/div')
        if img_list:
            for img in img_list:
                content.append(self.parse_img(response, img))

        news_tags = response.xpath('//div[@id="article-content"]/div/*|//div[@class="wsw"]/*|'
                                   '//div[@class="img-wrap"]//img|//div[@class="c-mmp__player"]/audio|'
                                   '//div[@class="c-mmp__player"]/video|'
                                   '//div[@class="intro m-t-md"]/p')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h3", "h5", "span", "p", "blockquote"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src", img_des="./@alt")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag == "audio":
                    con_media = self.parse_media(response, news_tag, media_type="mp3")
                    if con_media:
                        content.append(con_media)
                elif news_tag.root.tag == "video":
                    con_media = self.parse_media(response, news_tag, media_type="mp4")
                    if con_media:
                        content.append(con_media)
                elif news_tag.root.tag in ["ul", "ol"]:
                    for li in news_tag.xpath("./li"):
                        text_dict = self.parse_text(li)
                        if text_dict:
                            content.extend(text_dict)

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
                if x.strip():
                    dic['data'] = x.strip()
                    dic['type'] = 'text'
                    new_cons.append(dic)

        return new_cons

    def parseOneText(self, news_tag) -> list:
        """"
            一个标签下只有一段但是存在其他标签
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            if "".join(cons).strip():
                dic['data'] = "".join(cons).strip()
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag, img_xpath='./@src', img_des=''):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath(img_xpath).extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(img_des).extract_first() or None,
                   "src": img_url}
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
        videoUrl = news_tag.xpath("./@src|./@data-fallbacksrc").extract_first()
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
