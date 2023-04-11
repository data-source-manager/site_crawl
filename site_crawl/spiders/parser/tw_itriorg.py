# -*- coding: utf-8 -*-
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class Tw_itriorgParser(BaseParser):
    name = 'tw_itriorg'
    
    # 站点id
    site_id = "0101056a-2e8e-462a-a997-c370184b7ac4"
    # 站点名
    site_name = "工业技术研究院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "0101056a-2e8e-462a-a997-c370184b7ac4", "source_name": "工业技术研究院", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("912314a6-2f72-11ed-a768-d4619d029786", "产业情报", "https://www.itri.org.tw/ListStyle.aspx?DisplayStyle=15&SiteID=1&MmmID=1036461234426716651", "政治"),
            ("91231500-2f72-11ed-a768-d4619d029786", "最新新闻", "https://www.itri.org.tw/ListStyle.aspx?DisplayStyle=06&SiteID=1&MmmID=1036276263153520257", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            "//dl[@class='Bb_dotted sline']/dt/a/@href|//dl[@id='divContent']/dd/a[@class='title']/@href").extract() or ""
        if news_urls:
            for news_url in (news_urls):
                if not news_url.startswith('http'):
                    news_url = urljoin(response.url, news_url)
                yield news_url

    def get_title(self, response) -> str:
        title = response.xpath(
            "//article[@class='detail']/div[@id='title']/text()|//span[@id='spanTitle']/text()").extract_first(
            default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        author = []
        if "https://www.itri.org.tw/ListStyle.aspx?" in response.url:
            authors = response.xpath("//*[text()[contains(.,'工研院行銷傳播處')]]/text()[1]").extract() or []
            if authors:
                for author_a in authors:
                    author.append(author_a.replace("工研院行銷傳播處", "").strip())
        else:
            authors = response.xpath("//label[@class='jquerySelectorAuthorToLink']/text()").extract_first() or ""
            if authors:
                for author_a in authors.split("、"):
                    author.append(author_a.strip())
        return author

    def get_pub_time(self, response) -> str:

        time_str = response.xpath(
            "//li[@class='list-inline-item mr-3']/text()|//p[@id='pubDate']/text()").extract_first() or ""
        time_str = time_str.replace("日期：", "")
        dt_ = datetime_helper.fuzzy_parse_timestamp(time_str)
        if dt_:
            return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt_)))
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_node = response.xpath("//a[@class='domain-label']/text()").extract()
        return [tags for tags in tags_node]

    def get_content_media(self, response) -> list:
        content = []
        paragraph = ""
        news_tags = response.xpath(
            "//div[@id='divContent']/div[@class='run_around']/p/node()|//div[@id='divContent']/div[@class='run_around']/figure|//div[@class='detailContent']/node()|//div[@id='divContent']/figure[@class='big_img']")
        if news_tags:
            for news_tag in news_tags:
                if isinstance(news_tag.root, str):
                    if news_tag.root.strip():
                        text_dict = {"data": news_tag.root, "type": "text"}
                        if text_dict:
                            content.append(text_dict)
                    continue
                elif news_tag.root.tag == 'figure':
                    img_dict = self.parse_img(response, news_tag, xpath_src=".//img/@src",
                                              xpath_des=".//figcaption/text()")
                    content.append(img_dict)
                elif news_tag.root.tag in ["h1", "h2", "h3", "h4", 'h5', "strong", "p"]:
                    if news_tag.xpath(".//img"):
                        img_dict = self.parse_img(response, news_tag, xpath_src=".//img/@src",
                                                  xpath_des=".//img/@alt")
                        content.append(img_dict)
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
                else:
                    node_text = "".join(news_tag.xpath("./text()").extract())
                    paragraph += node_text.strip()
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if "延伸閱讀" in x.strip():
                    continue
                if x.strip():
                    new_cons.append(x.strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
                return dic

    def parse_img(self, response, news_tag, xpath_src='', xpath_des=''):
        if xpath_src:
            img_url = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(xpath_des).extract_first() if xpath_des else None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("//a[@class='entry_file_link']/@href").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": news_tag.xpath("//h2[@class='aside_h2']/text()").extract_first(),
            "description": news_tag.xpath("//h3[@class='entry_title entry_title__file']/text()").extract_first(),
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag, xpath_src='', xpath_des=''):
        video_src = urljoin(response.url, news_tag.xpath(xpath_src).extract_first())
        video_dic = {
            "type": "video",
            "src": video_src,
            "name": None,
            "description": news_tag.xpath(xpath_des).extract_first(),
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
        read_count_str = response.xpath("//li[@class='list-inline-item'][1]/text()").extract_first()
        read_count = 0
        if read_count_str:
            read_count = int(read_count_str)
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
