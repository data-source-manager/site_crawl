# -*- coding: utf-8 -*-
# fix(liyun:2023-01-06): 修正媒体资源后缀与源网页不一致(mp4->mp3) 
# fix(liyun:2023-01-07): 新增板块 


import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class UsaVoachineseParser(BaseParser):
    name = 'voachinese'
    
    # 站点id
    site_id = "7e1b44c2-7702-4788-b14f-086811b6e351"
    # 站点名
    site_name = "美国之音中文网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7e1b44c2-7702-4788-b14f-086811b6e351", "source_name": "美国之音中文网", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("662b4c6e-0eda-469c-9d66-e58e1c004698", "VOA卫视", "https://www.voachinese.com/z/1774", "政治"),
            ("4a8ac676-fe6f-11ec-a30b-d4619d029786", "中国", "https://www.voachinese.com/z/1757", "政治"),
            ("4a8ac6e4-fe6f-11ec-a30b-d4619d029786", "台湾", "https://www.voachinese.com/z/1769", "政治"),
            ("7d631c96-f67f-3f35-94cc-98d6c6291a78", "国际", "", "政治"),
            ("4a8b1bbc-fe6f-11ec-a30b-d4619d029786", "国际/中东", "https://www.voachinese.com/z/1759", "政治"),
            ("4a8ac7ca-fe6f-11ec-a30b-d4619d029786", "国际/亚太", "https://www.voachinese.com/z/1745", "政治"),
            ("4a8b1fc2-fe6f-11ec-a30b-d4619d029786", "国际/欧洲", "https://www.voachinese.com/z/1753", "政治"),
            ("4a8b23b4-fe6f-11ec-a30b-d4619d029786", "国际/美洲", "https://www.voachinese.com/z/1742", "政治"),
            ("4a8b2198-fe6f-11ec-a30b-d4619d029786", "国际/非洲", "https://www.voachinese.com/z/1741", "政治"),
            ("252e7a9d-01b3-46cf-96c1-8a36571e48dc", "揭谎频道", "https://www.voachinese.com/z/6352", "政治"),
            ("f5944e4e-14ac-4aea-b9ca-909b363523a1", "新闻采访及音频", "https://www.voachinese.com/z/1738", "政治"),
            ("4a8ac752-fe6f-11ec-a30b-d4619d029786", "港澳", "https://www.voachinese.com/z/1755", "政治"),
            ("b5a5a3fe-050c-470a-8fe5-46206ec87f67", "热点主题", "", "政治"),
            ("172834cd-d06c-4d36-90b5-891407f217ee", "热点主题/乌克兰局势", "https://www.voachinese.com/z/4012", "政治"),
            ("4a8b26fc-fe6f-11ec-a30b-d4619d029786", "热点主题/南中国海争端", "https://www.voachinese.com/z/2309", "政治"),
            ("4a8b268e-fe6f-11ec-a30b-d4619d029786", "热点主题/台海两岸关系", "https://www.voachinese.com/z/2371", "政治"),
            ("57499655-4e3d-4e9f-ba6f-490bb76a0103", "热点主题/国会报道", "https://www.voachinese.com/z/5142", "政治"),
            ("3ad999ae-e5e1-41bb-869a-a790463fb4b1", "热点主题/年终报道", "https://www.voachinese.com/z/3874", "政治"),
            ("36dbc453-d981-424b-99fe-8a1e05eb8794", "热点主题/新冠病毒疫情", "https://www.voachinese.com/z/5973", "政治"),
            ("4a8b2760-fe6f-11ec-a30b-d4619d029786", "热点主题/新疆西藏问题", "https://www.voachinese.com/z/2393", "政治"),
            ("06da927d-4448-4af5-ba5d-9e498c207ac8", "热点主题/新闻自由", "https://www.voachinese.com/z/5855", "政治"),
            ("4a8b2846-fe6f-11ec-a30b-d4619d029786", "热点主题/朝鲜半岛局势", "https://www.voachinese.com/z/2323", "政治"),
            ("4a8b259e-fe6f-11ec-a30b-d4619d029786", "热点主题/美中关系", "https://www.voachinese.com/z/1776", "政治"),
            ("e01fbb30-8688-4b0b-a440-d314796f6e12", "热点主题/美国之音专访", "https://www.voachinese.com/z/3596", "政治"),
            ("d20b7c3b-6cd0-407c-8299-64e9450a963d", "热点主题/难民问题", "https://www.voachinese.com/z/7111", "政治"),
            ("4a8ac5f4-fe6f-11ec-a30b-d4619d029786", "美国", "https://www.voachinese.com/z/1746", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "7e1b44c2-7702-4788-b14f-086811b6e351"

    def parse_list(self, response) -> list:
        if "2393" in response.url:
            news_urls = response.xpath(
                '//div[@class="col-xs-12 col-md-8 col-lg-8 pull-left content-offset"]//div[@class="row"]/ul/li/div/a/@href').extract() or ""
        else:
            news_urls = response.xpath('//div[@class="row"]/ul/li/div/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="title"]/@content').extract_first(default="")
        title = "".join(response.xpath('//meta[@name="title"]/@content').extract()).replace("时事大家谈：", "")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="Author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        time_ = response.xpath('//span[@class="date"]/time/@datetime').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        media_set = set()
        text_set = set()
        img_set = set()

        img_list = response.xpath('//div[@class="cover-media"]//img')
        if img_list:
            for img in img_list:
                con_img = self.parse_img(response, img)
                if con_img:
                    if con_img["src"] not in img_set:
                        img_set.add(con_img["src"])
                        content.append(con_img)
        video_src = response.xpath("//meta[@name='twitter:player:stream']/@content").get()
        if video_src:
            video_dic = {
                "src": video_src,
                "name": None,
                "description": None,
            }
            if video_src.endswith(".mp3"):
                video_dic["type"] = "audio"
                video_dic["md5src"] = self.get_md5_value(video_src) + ".mp3"
            else:
                video_dic["type"] = "video"
                video_dic["md5src"] = self.get_md5_value(video_src) + ".mp4"

            if video_dic["src"] not in media_set:
                media_set.add(video_dic["src"])
                content.append(video_dic)
        news_tags = response.xpath('//div[@id="article-content"]/div[@class="wsw"]/*|//div[@class="intro m-t-md"]/*')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        if text_dict[0]["data"] not in text_set:
                            text_set.add(text_dict[0]["data"])
                            content.extend(text_dict)
                if news_tag.root.tag == "a":
                    con_file = self.parse_file(response, news_tag)
                    if con_file:
                        content.append(con_file)

                if news_tag.root.tag == "div":
                    con_img = self.parse_img(response, news_tag.xpath(".//img"))
        category = response.xpath('//div[contains(@class,"media-pholder--audio")]/*')
        if category:
            for tag in category:
                img = tag.xpath(".//div[contains(@class,'c-mmp__poster')]/img")
                if img:
                    img_dict = self.parse_img(response, img)
                    if img_dict:
                        if img_dict["src"] not in img_set:
                            img_set.add(img_dict["src"])
                            content.append(img_dict)

                video = tag.xpath(".//div[@class='c-mmp__player']/audio")
                if video:
                    video_dict = self.parse_media(response, video, media_type="mp3")
                    if video_dict:
                        if video_dict["src"] not in media_set:
                            media_set.add(video_dict["src"])
                            content.append(video_dict)

                text_tag = tag.xpath('./p')
                if text_tag:
                    text_list = self.parse_text(text_tag)
                    if text_list:
                        if text_list[0]["data"] not in text_set:
                            text_set.add(text_list[0]["data"])
                            content.extend(text_list)
        else:
            img_list = response.xpath('//div[@class="cover-media"]//img')
            if img_list:
                for img in img_list:
                    con_img = self.parse_img(response, img)
                    if con_img:
                        if con_img["src"] not in img_set:
                            img_set.add(con_img["src"])
                            content.append(con_img)
            video_src = response.xpath("//meta[@name='twitter:player:stream']/@content").get()
            if video_src:
                video_dic = self.fix_media_file_format({
                    "type": "video",
                    "src": video_src,
                    "name": None,
                    "description": None,
                    "md5src": self.get_md5_value(video_src) + ".mp4"
                })
                if video_dic["src"] not in media_set:
                    media_set.add(video_dic["src"])
                    content.append(video_dic)
            news_tags = response.xpath(
                '//div[@id="article-content"]/div[@class="wsw"]/*|//div[@class="intro m-t-md"]/*')
            if news_tags:
                for news_tag in news_tags:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            if text_dict[0]["data"] not in text_set:
                                text_set.add(text_dict[0]["data"])
                                content.extend(text_dict)
                    if news_tag.root.tag == "a":
                        con_file = self.parse_file(response, news_tag)
                        if con_file:
                            content.append(con_file)

                    if news_tag.root.tag == "div":
                        con_img = self.parse_img(response, news_tag.xpath(".//img"))
                        if con_img:
                            if con_img["src"] not in img_set:
                                img_set.add(con_img["src"])
                                content.append(con_img)

        # 过滤异常正文数据
        content = [data for data in content if
                   not (data["type"] == "text" and data["data"].startswith("renderExternalContent"))]
        return content

    def get_detected_lang(self, response) -> str:
        return 'zh-cn'

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
                    if "弹出播放器" in x.strip() or "代码已经复制到剪贴板" in x.strip():
                        continue
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
            if "document" in oneCons or "function" in oneCons:
                return []
            if "弹出播放器" in oneCons or "代码已经复制到剪贴板" in oneCons:
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
        img = news_tag.xpath('./@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.attrib.get('alt').replace(".mp3", ""),
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
