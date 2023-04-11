# -*- coding: utf-8 -*-
# update:(liyun:2023-01-14) -> 新增板块
import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwCnaParser(BaseParser):
    name = 'cna'
    
    # 站点id
    site_id = "0f069484-9289-4687-942e-cfbf86d6dd0d"
    # 站点名
    site_name = "中央社"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "0f069484-9289-4687-942e-cfbf86d6dd0d", "source_name": "中央社", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e412c67b-0ab5-7fd2-9785-b9a03ff9afb2", "专题", "", "政治"),
            ("e2036582-9480-4578-83ec-25ab01c39d08", "专题/义务役恢复", "https://www.cna.com.tw/topic/newstopic/3803.aspx", "政治"),
            ("22d85f73-dafb-4b3e-9873-fd3df29b84a1", "专题/九合一选举查贿", "https://www.cna.com.tw/topic/newstopic/4101.aspx", "政治"),
            ("d2fc6e33-dc97-4da3-af74-4ae819b347f9", "专题/俄罗斯入侵乌克兰", "https://www.cna.com.tw/topic/newstopic/3506.aspx", "政治"),
            ("e0461756-441a-443a-a9aa-c468ec6dd8fa", "专题/全民共享发现", "https://www.cna.com.tw/topic/newstopic/4097.aspx", "政治"),
            ("68067811-6ef4-4233-b1cb-bba613f0cf12", "专题/平均地权条例", "https://www.cna.com.tw/topic/newstopic/4107.aspx", "政治"),
            ("9cbd3f4d-e76b-4bc9-bef1-81bce1125bdf", "专题/欧洲访台潮", "https://www.cna.com.tw/topic/newstopic/4108.aspx", "政治"),
            ("6d042882-02a2-48e1-bab4-ac9ce1247506", "专题/立委补选", "https://www.cna.com.tw/topic/newstopic/4078.aspx", "政治"),
            ("4a8ac400-fe6f-11ec-a30b-d4619d029786", "两岸", "https://www.cna.com.tw/list/acn.aspx", "政治"),
            ("4a8ac410-fe6f-11ec-a30b-d4619d029786", "产经", "https://www.cna.com.tw/list/aie.aspx", "经济"),
            ("1f795889-bf9b-4990-8b3c-1a5c9bfa568b", "即时", "https://www.cna.com.tw/list/aall.aspx", "政治"),
            ("4a8ac31a-fe6f-11ec-a30b-d4619d029786", "国际", "https://www.cna.com.tw/list/aopl.aspx", "政治"),
            ("ea27d599-fe57-49c2-8106-72df30efc971", "地方", "https://www.cna.com.tw/list/aloc.aspx", "政治"),
            ("4a8abf28-fe6f-11ec-a30b-d4619d029786", "政治", "https://www.cna.com.tw/list/aipl.aspx", "政治"),
            ("4a8ac4aa-fe6f-11ec-a30b-d4619d029786", "社会", "https://www.cna.com.tw/list/asoc.aspx", "社会"),
            ("4a8ac554-fe6f-11ec-a30b-d4619d029786", "科技", "https://www.cna.com.tw/list/ait.aspx", "科技"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "0f069484-9289-4687-942e-cfbf86d6dd0d"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//ul[@id="jsMainList"]/li/a/@href|//div[@class="itemVideo"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//article//h1/text()|'
                               '//div[@class="centralContent"]//h1//text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@itemprop="author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//meta[@itemprop="datePublished"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@class="articlekeywordGroup"]/div/a/text()').extract()
        if tags:
            for tag in tags:

                if tag.strip():
                    tags_list.append(tag.replace("#", "").strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        img_list = response.xpath('//div[@class="fullPic"]//div[@class="BGimgWrap"]/picture')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    content.append(con_img)

        news_tags = response.xpath('//div[contains(@class,"article-feed")]/article[1]//div[@class="paragraph"]/p|'
                                   '//div[contains(@class,"article-feed")]/article[1]//div[@class="paragraph"]//div[@class="BGimgWrap"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "div":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

        return content

    def get_detected_lang(self, response) -> str:

        return "zh-tw"

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

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip()
            if "公開播送或公開傳輸及利用" in oneCons:
                return []
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@data-src').extract_first() or news_tag.xpath('.//img/@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath('.//img/@alt').extract_first(),
                   "src": img_url
                   }
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
