import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


class UsaChathamhouseParser(BaseParser):
    name = 'chathamhouse'
    # 站点id
    site_id = "e3b15fe7-c29f-44ff-8ded-1ad16ed6bc82"
    # 站点名
    site_name = "查塔姆研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e3b15fe7-c29f-44ff-8ded-1ad16ed6bc82", "source_name": "查塔姆研究所", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("c085e23a-238a-452c-9574-d0f0c7622dbf", "国防与安全", "https://www.chathamhouse.org/topics/defence-and-security", "政治"),
            ("b0f99bfe-e2ec-3e5e-8d63-4b784a263648", "国防与安全/军备控制", "https://www.chathamhouse.org/search/content_format/Article/topic/arms-control-301", "政治"),
            ("0f6a9b22-a787-11ed-a74a-1094bbebe6dc", "国防与安全/北大西洋公约组织", "https://www.chathamhouse.org/search/content_format/Article/topic/north-atlantic-treaty-organization-nato-331", "政治"),
            ("29adb594-f8d0-466f-a2f4-5fd453ed65d6", "国防与安全/恐怖主义", "https://www.chathamhouse.org/search/content_format/Article/topic/terrorism-305", "政治"),
            ("26d24900-727a-5547-9a21-37fc62c22e66", "国防与安全/欧洲防御", "https://www.chathamhouse.org/search/content_format/Article/topic/european-defence-303", "政治"),
            ("0cde7727-c2df-445c-90eb-e54a5a3507ed", "国防与安全/毒品和有组织犯罪", "https://www.chathamhouse.org/search/content_format/Article/topic/drugs-and-organized-crime-302", "政治"),
            ("fc40ba77-42ec-3856-ad7c-9a728374b9a6", "国防与安全/维持和平与干预", "https://www.chathamhouse.org/search/content_format/Article/topic/peacekeeping-and-intervention-304", "政治"),
            ("f48f2b0a-a827-11ed-b64f-1094bbebe6dc", "大国", "", "政治"),
            ("a908afa1-5139-4ada-b551-b9758ab09188", "大国/中国国内政治", "https://www.chathamhouse.org/search/content_format/Article/topic/chinas-domestic-politics-502", "政治"),
            ("6354ce64-0884-599a-b38f-04983f8ba415", "大国/中国对外关系", "https://www.chathamhouse.org/search/content_format/Article/topic/chinas-relations-335", "政治"),
            ("77c0bc9b-02f2-3cba-9dcf-d489e5e3606e", "大国/美国外交政策", "https://www.chathamhouse.org/search/content_format/Article/topic/us-foreign-policy-337", "政治"),
            ("455f2f4c-cd55-31b7-ac18-aad64ed5d338", "大国/美国的国际角色", "https://www.chathamhouse.org/search/content_format/Article/topic/americas-international-role-334", "政治"),
            ("e700e1c4-7607-11ed-ad4d-d4619d029786", "政治与法律", "", "政治"),
            ("bfba7f9d-d90f-34b6-802b-2636071575ad", "政治与法律/人口统计和政治", "https://www.chathamhouse.org/search/content_format/Article/topic/demographics-and-politics-340", "政治"),
            ("52e24a88-a82e-11ed-9cce-1094bbebe6dc", "政治与法律/人权与安全", "https://www.chathamhouse.org/search/content_format/Article/topic/human-rights-and-security-341", "政治"),
            ("f3743b10-a82d-11ed-baa9-1094bbebe6dc", "政治与法律/名主和政治参与", "https://www.chathamhouse.org/search/content_format/Article/topic/democracy-and-political-participation-339", "政治"),
            ("f6480833-7d4e-390a-a3af-e99e5e24cdb6", "政治与法律/国际刑事司法", "https://www.chathamhouse.org/search/content_format/Article/topic/international-criminal-justice-342", "政治"),
            ("ef3ab7cd-7433-5d5d-a030-ab9b9fb4accc", "政治与法律/性别与平等", "https://www.chathamhouse.org/search/content_format/Article/topic/gender-and-equality-348", "政治"),
            ("a390722d-e1f9-50a4-8167-a7da5fafe6f4", "政治与法律/美国国内政治", "https://www.chathamhouse.org/search/content_format/Article/topic/us-domestic-politics-336", "政治"),
            ("0074008c-ffc0-407b-908a-e235ca83f739", "政治与法律/虚假信息", "https://www.chathamhouse.org/search/content_format/Article/topic/disinformation-354", "政治"),
            ("f35660bf-5c7d-4e6c-8b14-2b88221921f9", "政治与法律/难名和移民", "https://www.chathamhouse.org/search/content_format/Article/topic/refugees-and-migration-343", "政治"),
            ("b1b41be9-bafa-48b0-bd0c-79d593d94c75", "政治和法律", "https://www.chathamhouse.org/topics/politics-and-law", "政治"),
            ("d1c47ed8-a794-11ed-ae47-1094bbebe6dc", "经贸", "", "政治"),
            ("e02df972-a794-11ed-8253-1094bbebe6dc", "经贸/G7和G20", "https://www.chathamhouse.org/search/content_format/Article/topic/g7g8-and-g20-330", "政治"),
            ("25f86bef-a4c5-4ddf-b033-d97a1e6e4eb4", "经贸/世界贸易组织", "https://www.chathamhouse.org/search/content_format/Article/topic/world-trade-organization-wto-314", "政治"),
            ("0128a86a-8df1-4f7d-a652-dbf12de63846", "经贸/中国的一带一路倡议", "https://www.chathamhouse.org/search/content_format/Article/topic/chinas-belt-and-road-initiative-bri-309", "政治"),
            ("e63b87c1-827d-408b-b923-624bbe0b9407", "经贸/国际货币基金组织", "https://www.chathamhouse.org/search/content_format/Article/topic/international-monetary-fund-531", "政治"),
            ("c1c9bf0b-e4b5-5bdf-8da4-ad8fdf3f94c5", "经贸/国际贸易", "https://www.chathamhouse.org/search/content_format/Article/topic/international-trade-312", "政治"),
            ("faaa8009-0653-38b2-85f8-9f0bd9bb03ee", "经贸/国际金融体系", "https://www.chathamhouse.org/search/content_format/Article/topic/international-finance-system-311", "政治"),
            ("9caaaf59-c8cc-5223-80b1-600831c5acd8", "经贸/循环经济", "https://www.chathamhouse.org/search/content_format/Article/topic/circular-economy-317", "政治"),
            ("f277d058-a794-11ed-8d92-1094bbebe6dc", "经贸/投资非洲", "https://www.chathamhouse.org/search/content_format/Article/topic/investment-africa-313", "政治"),
            ("fa3247d5-e731-3448-b965-31b2df98fe17", "经贸/英国的全球角色", "https://www.chathamhouse.org/search/content_format/Article/topic/brexit-307", "政治"),
            ("67e93099-6b26-37d4-adbf-7a3ba7d1ae91", "经贸/金砖国家", "https://www.chathamhouse.org/search/content_format/Article/topic/brics-economies-308", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//section[@aria-labelledby="paragraph-211-title"]//div[@class="glide__slides"]//article/a/@href|'
            '//div[@class="views-row"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:

        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="wysiwyg"]/*|//div/iframe|//div[@class="artwork__wrapper"]/a|'
                                   '//div[@class="media__wrapper"]//img|'
                                   '//div[@class="hero__wysiwyg with-serif wysiwyg "]/p')
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
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
                        text_dict = self.parse_text(news_tag)
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
                    if news_tag.root.tag == "a":
                        con_media = self.parse_media(response, news_tag, media_type="mp3")
                        if con_media:
                            content.append(con_media)
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
                    new_cons.append({'data': "".join(con).strip().replace('\xa0', ''), 'type': "text"})
        return new_cons

    def parseOnetext(self, news_tag) -> list:
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip().replace('\xa0', '')
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
        videoUrl = news_tag.xpath("./@src|./@href").extract_first()
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
