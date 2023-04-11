import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class UsaSeiParser(BaseParser):
    name = 'sei'
    
    # 站点id
    site_id = "6f012eed-6571-4221-9209-abbd59c78795"
    # 站点名
    site_name = "卡内基梅隆大学软件工程研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "6f012eed-6571-4221-9209-abbd59c78795", "source_name": "卡内基梅隆大学软件工程研究所", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("2bc450d8-ab65-11ed-903f-1094bbebe6dc", "我们的工作", "", "政治"),
            ("0840b47b-da64-3ab3-ad47-d4388fc025aa", "我们的工作/所有话题", "https://www.sei.cmu.edu/our-work/all-topics/index.cfm", "政治"),
            ("f9ffe3c6-43bd-4b92-abe9-39f1df3a5a56", "所有时间", "", "政治"),
            ("db7b456c-a422-4d28-9287-67954691cdc4", "所有时间/企业风险和弹性管理", "https://www.sei.cmu.edu/our-work/enterprise-risk-resilience-management/index.cfm", "政治"),
            ("1828526d-7622-5eb4-ae7e-52d64a95654c", "所有时间/内部威胁", "https://www.sei.cmu.edu/our-work/insider-threat/index.cfm", "政治"),
            ("dd6f57bc-aea8-4887-ad91-58b9b5463dfb", "所有时间/安全开发", "https://www.sei.cmu.edu/our-work/secure-development/index.cfm", "政治"),
            ("a45678ec-0564-5bd5-a3a4-0ef6ffab1139", "所有时间/安全漏洞", "https://www.sei.cmu.edu/our-work/security-vulnerabilities/index.cfm", "政治"),
            ("12b803b2-ab6c-11ed-8c72-1094bbebe6dc", "所有时间/对情况的意识", "https://www.sei.cmu.edu/our-work/situational-awareness/index.cfm", "政治"),
            ("f6305209-92e2-346b-9876-2f8325c3c8ca", "所有时间/恶意软件分析的逆向工程", "https://www.sei.cmu.edu/our-work/reverse-engineering-for-malware-analysis/index.cfm", "政治"),
            ("546a65ae-bfb2-3a17-be0f-80f3bf3526bc", "所有时间/软件结构", "https://www.sei.cmu.edu/our-work/software-architecture/", "政治"),
            ("2a9b58cd-220b-31e1-a2cb-4b463e369902", "所有时间/边缘计算", "https://www.sei.cmu.edu/our-work/edge-computing/index.cfm", "政治"),
            ("06688f3c-ab6c-11ed-af3a-1094bbebe6dc", "所有时间/量子计算", "https://www.sei.cmu.edu/our-work/quantum-computing/index.cfm", "政治"),
            ("4be80ac1-abf0-250f-d575-580eedb34f8f", "所有话题", "", "政治"),
            ("4a8bfe62-ab65-11ed-b504-1094bbebe6dc", "所有话题/云计算", "https://www.sei.cmu.edu/our-work/cloud-computing/index.cfm", "政治"),
            ("7df47380-5ccb-57a0-a6db-5717480da277", "所有话题/人工智能工程", "https://www.sei.cmu.edu/our-work/artificial-intelligence-engineering/index.cfm", "政治"),
            ("984c9715-802c-4ac6-bd63-abb389f92929", "所有话题/敏捷", "https://www.sei.cmu.edu/our-work/agile/index.cfm", "政治"),
            ("15d0314b-d701-3ab3-87b0-694d594f966d", "所有话题/网络安全工程", "https://www.sei.cmu.edu/our-work/cybersecurity-engineering/index.cfm", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="CS_Textblock_Text"]/h3/a/@href|'
                                   '//div[@class="card"]//h4/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h2[contains(@class,"topic-name")]/text()|'
                               '//meta[@name="sei_title"]/@content|//meta[@name="ajs-page-title"]/@content|'
                               '//h1[@id="title-text"]//font/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@name="pubdate"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[contains(@id,"cs_control")]/div[@class="CS_Textblock_Text"]/*|'
                                   '//div[@class="col-md-8"]/*|//main[contains(@class,"col-md-8")]/*|'
                                   '//iframe[contains(@src,"youtube")]|//div[@class="assetSingleMain"]/*|'
                                   '//div[@class="blog-post"]/*|//p[@class="lead-body"]|'
                                   '//div[@class="innerCell"]/*|//div[@class="content-wrapper"]/p/span/a')
        if news_tags:
            for news_tag in news_tags:
                if type(news_tag.root) == str:
                    con = news_tag.root.strip()
                    if con:
                        content.append({
                            "type": "text",
                            "data": con
                        })
                else:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "a"]:
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            content.extend(text_dict)
                    if news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            con_text = self.parseOnetext(con)
                            if con_text:
                                content.extend(con_text)
                    if news_tag.root.tag == "a":
                        con_file = self.parse_file(response, news_tag)
                        if con_file:
                            content.append(con_file)
                    if news_tag.root.tag == "iframe":
                        con_media = self.parse_media(response, news_tag, media_type="mp4")
                        if con_media:
                            content.append(con_media)

                    if news_tag.root.tag == "img":
                        con_img = self.parse_single_img(response, news_tag)
                        if con_img:
                            content.extend(con_img)

        return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

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
            oneCons = "".join(cons).strip().replace('\xa0', '').replace('\n', '')
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
