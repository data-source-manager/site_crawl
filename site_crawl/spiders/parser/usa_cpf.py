# -*- coding: utf-8 -*-
# update: liyun 2023-01-10 -> 新增板块与解析代码变更
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.tools import check_img


class UsaCpfParser(BaseParser):
    name = 'cpf'
    
    # 站点id
    site_id = "9f097c29-7ecb-4c4e-8b9a-fdf895f5d44b"
    # 站点名
    site_name = "美国太平洋舰队司令部官网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "9f097c29-7ecb-4c4e-8b9a-fdf895f5d44b", "source_name": "美国太平洋舰队司令部官网", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("1a18a156-2186-e756-33b9-2ea9c1d33862", "编辑部", "", "政治"),
            ("0d7dbacd-b5bf-45f2-ad05-cb50f1282250", "编辑部/消息", "https://www.cpf.navy.mil/Newsroom/News/", "军事"),
            ("2ccbf08b-7d54-4cf7-b225-a5a69af0bd27", "编辑部/演讲", "https://www.cpf.navy.mil/Newsroom/Speeches/", "军事"),
            ("1b5840e2-1ce3-4adb-9f92-c187b4a69e06", "编辑部/读数", "https://www.cpf.navy.mil/Newsroom/Readouts/", "军事"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "9f097c29-7ecb-4c4e-8b9a-fdf895f5d44b"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="a-summary"]/a/@href'
            '|//div[@id="dnn_ctr92951_ModuleContent"]//ul//li/a/@href'
            '|//div[@id="dnn_ctr92951_Dashboard_ph"]//ul//li/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return [response.xpath('//h2[@class="author"]/text()').extract_first(default="").strip()]

    def get_pub_time(self, response) -> str:
        try:
            _time = response.xpath('//div[@class="press-briefing__date"]/text()').extract_first(default="")
            d, m, y = _time.strip().split(" ")

            def transf_month(m):
                months = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                          "October", "November", "December"]
                return {months[i]: (f'0{i + 1}' if i + 1 < 10 else f'{i + 1}') for i in range(len(months))}.get(m)

            return f"{y}-{transf_month(m)}-{d.strip(',')} 00:00:00"
        except:
            import traceback
            print(traceback.format_exc())
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags = response.xpath('//ul[@class="tags"]/a/text()').extract()
        return [a.strip() for a in tags]

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@class="acontent-container"]/*'
            '|//div[@class="acontent-container"]/text()'
            '|//div[@class="image-wrapper"]/img'
        ) or []
        for news_tag in news_tags:
            if type(news_tag.root) == str:
                text = news_tag.root.strip()
                text and content.append({"data": text, "type": "text"})
            elif news_tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text_dict = self.parseOnetext(news_tag)
                if text_dict:
                    content.extend(text_dict)
            elif news_tag.root.tag == "ul":
                for con in news_tag.xpath('./li'):
                    con_text = self.parseOnetext(con)
                    if con_text:
                        content.extend(con_text)
            elif news_tag.root.tag == "img":
                con_img = self.parse_single_img(response, news_tag)
                if con_img:
                    content.extend(con_img)

        # news_tags = response.xpath('//div[@class="acontent-container"]/text()|'
        #                            '//div[@class="acontent-container"]/div[contains(@class,"media-inline")]|'
        #                            '//div[@class="acontent-container"]/p')
        # if news_tags:
        #     for news_tag in news_tags:
        #         if type(news_tag.root) == str:
        #             con_text = news_tag.root
        #             if con_text.strip():
        #                 dic = {
        #                     "type": "text",
        #                     "data": con_text.strip()
        #                 }
        #                 content.append(dic)
        #         else:
        #             if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
        #                 text_dict = self.parse_text(news_tag)
        #                 if text_dict:
        #                     content.extend(text_dict)
        #             if news_tag.root.tag == "div":
        #                 con_img = self.parse_img(response, news_tag)
        #                 if con_img:
        #                     content.append(con_img)

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
                   "description": news_tag.attrib.get('alt'),
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
