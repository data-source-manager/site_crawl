# -*- coding: utf-8 -*-
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser

"""
    模版
"""


class TwTpofParser(BaseParser):
    name = 'tpof'
    
    # 站点id
    site_id = "a20f5ef3-c2a6-4a11-b4f4-dfda848e490e"
    # 站点名
    site_name = "台湾民意基金会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "a20f5ef3-c2a6-4a11-b4f4-dfda848e490e", "source_name": "台湾民意基金会", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8c31c8-fe6f-11ec-a30b-d4619d029786", "两岸关系", "", "政治"),
            ("eaf54df3-d664-40b7-a26a-7cf9bea3baab", "两岸关系/两岸交流", "https://www.tpof.org/category/%e5%85%a9%e5%b2%b8%e9%97%9c%e4%bf%82/%e5%85%a9%e5%b2%b8%e4%ba%a4%e6%b5%81/", "政治"),
            ("721e3dd8-0645-40a3-bebe-e922468f804a", "两岸关系/两岸军事", "https://www.tpof.org/category/%e5%85%a9%e5%b2%b8%e9%97%9c%e4%bf%82/%e5%85%a9%e5%b2%b8%e8%bb%8d%e4%ba%8b/", "政治"),
            ("b929eebc-6984-4fa1-a351-98e70d6ab5f4", "两岸关系/两岸政治", "https://www.tpof.org/category/%e5%85%a9%e5%b2%b8%e9%97%9c%e4%bf%82/%e5%85%a9%e5%b2%b8%e6%94%bf%e6%b2%bb/", "政治"),
            ("c10ffd63-6b98-4198-883a-79ebf71d3960", "两岸关系/两岸经贸", "https://www.tpof.org/category/%e5%85%a9%e5%b2%b8%e9%97%9c%e4%bf%82/%e5%85%a9%e5%b2%b8%e7%b6%93%e8%b2%bf/", "政治"),
            ("4a8c322c-fe6f-11ec-a30b-d4619d029786", "台湾政治", "", "政治"),
            ("09ab34aa-87c1-472b-86a0-455cc36a36cf", "台湾政治/公共政策", "https://www.tpof.org/category/%e5%8f%b0%e7%81%a3%e6%94%bf%e6%b2%bb/%e5%85%ac%e5%85%b1%e6%94%bf%e7%ad%96/", "政治"),
            ("aedb1451-b014-4135-8dc6-4ce1990069fd", "台湾政治/国家认同", "https://www.tpof.org/category/%e5%8f%b0%e7%81%a3%e6%94%bf%e6%b2%bb/%e5%9c%8b%e5%ae%b6%e8%aa%8d%e5%90%8c/", "政治"),
            ("dddb0ac4-820a-4778-beed-edf1facdea60", "台湾政治/宪政体制", "https://www.tpof.org/category/%e5%8f%b0%e7%81%a3%e6%94%bf%e6%b2%bb/%e6%86%b2%e6%94%bf%e9%ab%94%e5%88%b6/", "政治"),
            ("729664f4-4d25-496e-a739-d83d9fffa8e9", "台湾政治/总统声望", "https://www.tpof.org/category/%e5%8f%b0%e7%81%a3%e6%94%bf%e6%b2%bb/%e7%b8%bd%e7%b5%b1%e8%81%b2%e6%9c%9b/", "政治"),
            ("4a8c329a-fe6f-11ec-a30b-d4619d029786", "国防外交", "", "政治"),
            ("503058e0-6e67-3178-8e77-e8d87073cd8e", "国防外交/台日关系", "https://www.tpof.org/category/%e5%9c%8b%e9%98%b2%e5%a4%96%e4%ba%a4/%e5%8f%b0%e6%97%a5%e9%97%9c%e4%bf%82/", "政治"),
            ("22614477-b821-306a-8d72-9ba7dd3d5781", "国防外交/台欧关系", "https://www.tpof.org/category/%e5%9c%8b%e9%98%b2%e5%a4%96%e4%ba%a4/%e5%8f%b0%e6%ad%90%e9%97%9c%e4%bf%82/", "政治"),
            ("408b8dad-f691-3ffb-9cd4-7c79d1acad59", "国防外交/台美关系", "https://www.tpof.org/category/%e5%9c%8b%e9%98%b2%e5%a4%96%e4%ba%a4/%e5%8f%b0%e7%be%8e%e9%97%9c%e4%bf%82/", "政治"),
            ("dd11086f-8741-3c03-b45d-af4de84b5bee", "国防外交/国防", "https://www.tpof.org/category/%e5%9c%8b%e9%98%b2%e5%a4%96%e4%ba%a4/%e5%9c%8b%e9%98%b2/", "政治"),
            ("9040bdab-0cb2-3efc-85df-eaf348e45ac5", "国防外交/外交", "https://www.tpof.org/category/%e5%9c%8b%e9%98%b2%e5%a4%96%e4%ba%a4/%e5%a4%96%e4%ba%a4/", "政治"),
            ("512efece-9326-11ed-85ea-1094bbebe6dc", "税制", "", "政治"),
            ("734eb0d7-13a0-4a65-9514-4a5f29ae9865", "税制/产业政策", "https://www.tpof.org/category/%e8%b2%a1%e7%b6%93%e5%8b%95%e6%85%8b/%e7%94%a2%e6%a5%ad%e6%94%bf%e7%ad%96/", "政治"),
            ("6b8fe1ef-1c10-3eac-9217-093964f2b1e0", "税制/经济发展", "https://www.tpof.org/category/%e8%b2%a1%e7%b6%93%e5%8b%95%e6%85%8b/%e7%b6%93%e6%bf%9f%e7%99%bc%e5%b1%95/", "政治"),
            ("4a8c3420-fe6f-11ec-a30b-d4619d029786", "选举", "", "政治"),
            ("1a0cd725-5bf9-458c-80d5-fc12da40bb62", "选举/六都市长选举", "https://www.tpof.org/category/%e9%81%b8%e8%88%89/%e5%85%ad%e9%83%bd%e5%b8%82%e9%95%b7%e9%81%b8%e8%88%89/", "政治"),
            ("265e5e5f-ec20-4538-a52d-846f7499e6e8", "选举/县市议员选举", "https://www.tpof.org/category/%e9%81%b8%e8%88%89/%e7%b8%a3%e5%b8%82%e8%ad%b0%e5%93%a1%e9%81%b8%e8%88%89/", "政治"),
            ("12b36b24-d838-4109-9398-154f46b77647", "选举/县市长选举", "https://www.tpof.org/category/%e9%81%b8%e8%88%89/%e7%b8%a3%e5%b8%82%e9%95%b7%e9%81%b8%e8%88%89/", "政治"),
            ("bd2c7ddf-9b06-403b-a7cc-f474fa80b92d", "选举/总统选举", "https://www.tpof.org/category/%e9%81%b8%e8%88%89/%e7%b8%bd%e7%b5%b1%e9%81%b8%e8%88%89/", "政治"),
            ("37bae163-0ffc-4c41-91d5-01d78d383ced", "选举/立委选举", "https://www.tpof.org/category/%e9%81%b8%e8%88%89/%e7%ab%8b%e5%a7%94%e9%81%b8%e8%88%89/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = 'a20f5ef3-c2a6-4a11-b4f4-dfda848e490e'

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="infor-listing"]/a/@href').extract() or ""
        if news_urls:
            for news_url in news_urls:
                url = urljoin(response.url, news_url)
                if "www.tpof.org" in url:
                    yield url

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="tittle"]/h3/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        """
        时间泛解析直接转标准格式存在一定问题 先采用转时间戳在转标准的方式
        """
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="post-content"]/*|'
                                   '//div[@class="post-content"]//figure[@class="wpb_wrapper vc_figure"]')
        if news_tags:
            for news_tag in news_tags:
                if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                    text_dict = self.parseOnetext(news_tag)
                    if text_dict:
                        content.extend(text_dict)
                if news_tag.root.tag == "ul":
                    for con in news_tag.xpath('./li'):
                        con_text = self.parseOnetext(con)
                        if con_text:
                            content.extend(con_text)

                if news_tag.root.tag == "figure":
                    con_img = self.parse_img(response, news_tag)
                    if con_img:
                        content.append(con_img)

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

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        img = news_tag.xpath('.//img/@src').extract_first()
        if img:
            img_url = urljoin(response.url, img)
            dic = {"type": "image",
                   "name": news_tag.attrib.get('title', None),
                   "md5src": self.get_md5_value(img_url) + '.jpg',
                   "description": "".join(news_tag.xpath('.//figcaption//text()').extract()).strip(),
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
        videoUrl = news_tag.xpath("").extract_first()
        if media_type == "video":
            suffix = ".mp4"
        else:
            suffix = ".mp3"
        if videoUrl:
            video_src = urljoin(response.url, videoUrl)
            video_dic = {
                "type": "video",
                "src": video_src,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(video_src) + suffix
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
