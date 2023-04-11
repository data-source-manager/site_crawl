# -*- coding: utf-8 -*-
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal.datetime_helper import parseTimeWithOutTimeZone


class JpchinakyodonewsParser(BaseParser):
    name = 'jp_chinakyodonews'
    
    # 站点id
    site_id = "4b76890f-7037-4c7c-9d96-8cb20d922173"
    # 站点名
    site_name = "共同社中文网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "4b76890f-7037-4c7c-9d96-8cb20d922173", "source_name": "共同社中文网", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8b3c0a-fe6f-11ec-a30b-d4619d029786", "中日关系", "https://china.kyodonews.net/news/japan-china_relationship", "政治"),
            ("4a8b3bba-fe6f-11ec-a30b-d4619d029786", "全球纵横", "https://china.kyodonews.net/news/global_news", "政治"),
            ("4a8b3c5a-fe6f-11ec-a30b-d4619d029786", "日本政治", "https://china.kyodonews.net/news/japan_politics", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//ul[@id='js-postListItems']/li/a/@href").extract() or ""
        time_list = response.xpath("//ul[@id='js-postListItems']/li/p/text()[normalize-space()]").getall() or []

        if news_urls:
            for index, news_url in enumerate(news_urls):
                item_url = urljoin(response.url, news_url)
                self.Dict[item_url] = time_list[index]
                yield item_url

    def get_title(self, response) -> str:
        title = response.xpath("//div[@class='main']/h1/text()").extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        2023年 3月 6日 - 15:27
        """
        time_ = self.Dict[response.url]
        if time_:
            time_ = datetime.strptime(time_.replace("|", "").strip(), "%Y年 %m月 %d日 - %H:%M")
            return parseTimeWithOutTimeZone(time_, site_name="共同社中文网")
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='article-body']/*|//div[@class='mainpic photo-caption']//img")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@data-src",
                                             img_des="./following-sibling::div/span/text()")
                    if con_img:
                        content.append(con_img)
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

    def parse_img(self, response, news_tag, img_xpath='', img_des=''):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath(img_xpath).extract_first()

        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(img_des).get() or None,
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

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath("./@src").extract_first()
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
        like_count = 0
        return like_count

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
