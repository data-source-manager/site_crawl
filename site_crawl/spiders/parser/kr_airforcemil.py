# -*- coding: utf-8 -*-
import time
from urllib.parse import unquote
from urllib.parse import urljoin

import jsonpath
import requests

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class KR_airforcemilParser(BaseParser):
    name = 'kr_airforcemil'
    
    # 站点id
    site_id = "4aaa3e32-c4ca-48ff-8072-4da91ffc1048"
    # 站点名
    site_name = "韩国空军"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "4aaa3e32-c4ca-48ff-8072-4da91ffc1048", "source_name": "韩国空军", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4351af14-4fe3-426b-817f-9b86786557c6", "讯息", "https://www.airforce.mil.kr/user/indexSub.action?codyMenuSeq=156893231&siteId=last2&menuUIType=sub", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        headers = {
            'Accept': 'application/json;odata=verbose',
            'Referer': 'https://www.aeronautica.difesa.it/comunicazione/pubinfo/comstampa/Pagine/default.aspx',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36',
        }
        api_url = 'https://www.aeronautica.difesa.it/_api/search/query?QueryText=%27*+webid:%22b074e7e0-9558-471c-a50e-0aa18c217fa5%22%27&RefinementFilters=%27and(ContentType:AMIComunicatoStampaPage,AMIDataComunicato:range(1899-12-31T15:54:17Z,2040-12-31T15:59:59Z,to=%22le%22,from=%22ge%22))%27&TrimDuplicates=false&SortList=%27AMIDataComunicato:descending%27&StartRow=0&RowsPerPage=10&RowLimit=10&selectproperties=%27ListItemID,AMILuogo,AMIDataComunicato,Title,Path%27&QueryTemplatePropertiesUrl=%27spfile://webroot/queryparametertemplate.xml%27'
        json_data = requests.get(api_url, headers=headers).json()
        news_urls = jsonpath.jsonpath(json_data, "$..results[?(@.Key=='Path')].Value")
        pub_times = jsonpath.jsonpath(json_data, "$..results[?(@.Key=='AMIDataComunicato')].Value")
        if news_urls:
            for index, news_url in enumerate(news_urls):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                self.Dict[news_url] = pub_times[index]
                yield news_url

    def get_title(self, response) -> str:
        titles = response.xpath(
            "//span[contains(@id,'ctl00_PlaceHolderMain_TitoloComunicato_TitoloRiga')]/text()[normalize-space()]").extract()

        if titles:
            title = "".join(titles)
            return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []
        return author_list

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        datePublished_str = self.Dict[unquote(response.url, "utf-8")]
        if datePublished_str:
            dt = datetime_helper.fuzzy_parse_timestamp(datePublished_str)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(dt)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[contains(@class,'ami-notizia-principale-')]/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h3", "h5", "span", "p", "blockquote"] and news_tag.root.get("class",
                                                                                                      "") != 'article-meta':
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag == "img":
                    con_img = self.parse_img(response, news_tag, img_xpath="./@src", img_des="./@alt")
                    if con_img:
                        content.append(con_img)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        """"
            可以对一个标签下存在多个段落进行解析
        """
        dic = {}
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'

        return dic

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
                   "description": news_tag.xpath(img_des).extract_first() or None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        fileUrl = news_tag.xpath("./self::a[contains(@href,'.pdf')]/@href").extract_first()
        if fileUrl:
            file_src = urljoin(response.url, fileUrl)
            file_dic = {
                "type": "file",
                "src": file_src,
                "name": news_tag.xpath("./self::a[contains(@href,'.pdf')]/text()").get() or None,
                "description": None,
                "md5src": self.get_md5_value(file_src) + ".pdf"
            }
            return file_dic

    def parse_media(self, response, news_tag):
        videoUrl = news_tag.xpath(".//iframe/@src").extract_first()
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
        comment_count = 0
        return comment_count

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        return repost_source
