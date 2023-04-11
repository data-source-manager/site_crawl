# -*- coding: utf-8 -*-
import re
import time
from urllib.parse import urljoin

from util.time_deal import datetime_helper
from .base_parser import BaseParser


class CN_12371Parser(BaseParser):
    name = 'cn_12371'
    
    # 站点id
    site_id = "ac147652-d34f-45e5-8e1c-3de302b51cde"
    # 站点名
    site_name = "共产党网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "ac147652-d34f-45e5-8e1c-3de302b51cde", "source_name": "共产党网", "direction": "cn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8e0e1c-fe6f-11ec-a30b-d4619d029786", "中共中央政治局会议", "https://www.12371.cn/special/zzjhy/", "政治"),
            ("4a8e0db8-fe6f-11ec-a30b-d4619d029786", "习近平讲话", "https://www.12371.cn/special/xxzd/jh/", "政治"),
            ("64a6ae90-9fa4-4c03-96ee-ae98861596ab", "党员教育", "", "政治"),
            ("204329ab-65a2-4c2e-a6e3-8ece41db3d08", "党员教育/典型案例", "https://www.12371.cn/dyjytx/dxal/", "政治"),
            ("764e4290-3b64-49dd-bdf6-89d02e31bef1", "党员教育/工作动态", "https://www.12371.cn/dyjytx/zygz/", "政治"),
            ("06297dea-e65f-4ccf-ba98-5a43092b1035", "党员教育/政策文件", "https://www.12371.cn/dyjytx/zcwj/", "政治"),
            ("ea16c9be-91d4-49f7-86ce-4ad8e638c5b4", "党员教育/经验教育", "https://tougao.12371.cn/liebiao.php?fid=111&filter=typeid&typeid=26", "政治"),
            ("e24822b8-4ed5-4fa8-8e97-d1bae4943fe9", "党的历史", "", "政治"),
            ("4d0c98f3-38f7-4afb-b655-14e2855464f7", "党的历史/先进典型", "https://www.12371.cn/special/dzby/", "政治"),
            ("b0e64787-9ad0-4094-98c7-a556ddebac0a", "党的历史/光辉历程", "https://www.12371.cn/dsxx/xds/", "政治"),
            ("b0960545-85ce-4d81-a83e-0bf0d6767c03", "党的历史/创新理论", "https://www.12371.cn/dsxx/wsx/", "政治"),
            ("0f7ac0f9-bab4-444c-8afb-9abdf3bdadd5", "党的历史/学习研讨", "https://www.12371.cn/dsxx/pl/", "政治"),
            ("a834a658-66f2-486b-b5b9-2aac0279c56f", "党的历史/进展成效", "https://www.12371.cn/dsxx/dt/", "政治"),
            ("3753488a-773b-4e20-bba8-8b2d6a2288a5", "党的历史/重要部署", "https://www.12371.cn/dsxx/bs/", "政治"),
            ("58591267-ba8b-4551-811d-aa9ebc16383b", "党章党规", "", "政治"),
            ("7d73c0f9-238c-4190-add4-ea0340780840", "党章党规/准则", "https://www.12371.cn/special/dnfg/", "政治"),
            ("163f1465-1d5b-420a-b68f-54965637f5f6", "党章党规/办法", "https://www.12371.cn/special/dnfg/bf/", "政治"),
            ("729a8523-1a42-4fab-87d0-dd041543e735", "党章党规/固定", "https://www.12371.cn/special/dnfg/gd/", "政治"),
            ("4a59a88e-dc2e-432e-81b8-e3d300ea07d0", "党章党规/条例", "https://www.12371.cn/special/dnfg/tl/", "政治"),
            ("fb25fb1c-8f38-4bd2-950f-dac558a16e69", "党章党规/细则", "https://www.12371.cn/special/dnfg/xz/", "政治"),
            ("3c064217-764c-49f5-9f31-d2437d89ef34", "党章党规/规则", "https://www.12371.cn/special/dnfg/bf/", "政治"),
            ("6de0c4a1-9765-46e8-a6ab-f79279f44cce", "党章党规/规范性文件", "https://www.12371.cn/special/zcwj/", "政治"),
            ("722d1f7a-2e49-4fe1-a810-7fd2d86f25d0", "思想理论", "https://www.12371.cn/special/sxll/", "政治"),
            ("4a8e0e58-fe6f-11ec-a30b-d4619d029786", "政治局集体会议", "https://www.12371.cn/special/lnzzjjtxx/", "政治"),
            ("3fd97fc3-5c03-4116-9566-49538cbba960", "组织工作", "", "政治"),
            ("0f38bac4-d49e-4f1b-aa2f-e24366486544", "组织工作/人事任免", "https://www.12371.cn/special/rsrm/", "政治"),
            ("de794e27-4511-4564-9c94-fd6ea3920d26", "组织工作/仲祖文专栏", "https://news.12371.cn/dzybmbdj/zzb/zzw/", "政治"),
            ("8f487821-1afc-4232-9fbf-58670844f0d2", "组织工作/工作动态", "https://news.12371.cn/dzybmbdj/zzb/gzdt/", "政治"),
            ("437cc1c4-0125-4342-8aa1-61689e1aed98", "组织工作/成就经验", "https://news.12371.cn/dzybmbdj/zzb/cj/", "政治"),
            ("573e4ec5-d883-4b56-a6ca-7dcff7222528", "组织工作/政策解读", "https://news.12371.cn/dzybmbdj/zzb/zcjd/", "政治"),
            ("28ae0fe9-d601-4872-8b3f-9b4ad9a3f582", "组织工作/组工文件", "https://www.12371.cn/special/zgwjk/", "政治"),
            ("39de5aac-55ab-4287-8974-fef4d98edab9", "组织工作/统计公报", "https://news.12371.cn/dzybmbdj/zzb/dntjgb/", "政治"),
            ("460daa36-4d53-44c1-af56-49ae750b8368", "组织工作/领导活动", "https://news.12371.cn/dzybmbdj/zzb/ldhd/", "政治"),
            ("4a8e0dea-fe6f-11ec-a30b-d4619d029786", "评论", "https://www.12371.cn/special/xxzd/wk/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath("//ul[@class='showMoreNChildren']/li//a/@href|"
                                   "//ul[@class='ul_list']/li//a/@href|"
                                   "//h4/a/@href|"
                                   "//div[@id='showMoreNChildren']/ul/li//a/@href|"
                                   "//ul[@class='dyw981_text']/li/a/@href|"
                                   "//div[@id='active_md']/ul/li//a/@href|"
                                   "//div[contains(@class,'three_listtext')]/ul/li/a/@href").extract() or []
        if len(news_urls) == 0:
            news_urls = re.findall("'link_add':'(.*?)'", response.text)
        for news_url in news_urls:
            url = urljoin(response.url, news_url)
            if "www.12371.cn" in url:
                yield url

    def get_title(self, response) -> str:
        title = response.xpath("//h1[@class='big_title']/text()[normalize-space()]").extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_author(self, response) -> list:
        authors = []
        authorFiled = response.xpath("//i[@class='time']/text()").get()
        if authorFiled:
            author = re.findall("编辑：([\u4e00-\u9fa5]+)", authorFiled)
            if author:
                authors.append(author[0])
        return authors

    def get_pub_time(self, response) -> str:
        time_ = response.xpath("//i[@class='time']/text()").get()
        if time_:
            year, mt, dy, hor = re.findall("发布时间：(\d{4})年(\d{2})月(\d{2})日 (\d{2}:\d{2})", time_)[0]
            Date_str = year + "-" + mt + "-" + dy + " " + hor
            if Date_str:
                dt = datetime_helper.fuzzy_parse_timestamp(Date_str)
                return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(dt)))
            else:
                return "9999-01-01 00:00:00"
        else:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []
        return tags_list

    def get_content_media(self, response) -> list:
        content = []
        news_tags = response.xpath("//div[@class='word']/*")
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h4", "strong", "p"]:
                    text_dict = self.parse_text(news_tag)
                    if text_dict:
                        content.append(text_dict)
                elif news_tag.root.tag in ["ul", "ol"]:
                    traversal_node = news_tag.xpath("./li")
                    for li in traversal_node:
                        text_dict = self.parse_text(li)
                        content.append(text_dict)
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

    def parse_text(self, news_tag):
        dic = {}
        cons = news_tag.xpath('.//text()').extract() or ""
        new_cons = []
        if cons:
            for x in cons:
                if x.strip():
                    new_cons.append(x.replace("\n", "").replace("\r", "").strip())
            new_cons = ''.join([c for c in new_cons if c != ""])
            if new_cons:
                dic['data'] = new_cons
                dic['type'] = 'text'
        return dic

    def parse_img(self, response, news_tag, img_xpath='', des_xpath=''):
        img_url = urljoin(response.url, news_tag.xpath(img_xpath).extract_first())
        if img_url:
            dic = {"type": "image",
                   "name": None,
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": news_tag.xpath(des_xpath).get() or None if des_xpath else None,
                   "src": img_url}
            return dic

    def parse_file(self, response, news_tag):
        file_src = urljoin(response.url, news_tag.xpath("").extract_first())
        file_dic = {
            "type": "file",
            "src": file_src,
            "name": None,
            "description": None,
            "md5src": self.get_md5_value(file_src) + ".pdf"
        }
        return file_dic

    def parse_media(self, response, news_tag):
        video_src = urljoin(response.url,
                            news_tag.xpath(".//self::iframe[contains(@src,'youtube')]/@src").extract_first())
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
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        if self.Dict.get(response.url):
            return True
        return False

    def get_repost_source(self, response) -> str:
        repost_source = ""
        repost = response.xpath("//i[@class='time']/text()").get()
        if repost:
            repost_source_str = re.findall("来源：([\u4e00-\u9fa5]+)", repost)
            if repost_source_str:
                self.Dict[response.url] = repost_source_str[0]
                repost_source = repost_source_str[0].replace("来源：", "")
        return repost_source
