import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


class JpJiiaParser(BaseParser):
    name = 'jiia'
    
    # 站点id
    site_id = "42891bb7-2983-4975-a177-ab9bb089f364"
    # 站点名
    site_name = "日本国际问题研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "42891bb7-2983-4975-a177-ab9bb089f364", "source_name": "日本国际问题研究所", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("4a8f7b76-fe6f-11ec-a30b-d4619d029786", "报告", "https://www.jiia.or.jp/column/archive.html", "政治"),
            ("0de87dd7-6ea7-5d05-00db-26db3d84bb5e", "研究活动", "", "政治"),
            ("3b855560-f4e8-b7e0-90dd-1446f4db5684", "研究活动/中东", "", "政治"),
            ("51f10fef-3653-4711-93f2-e3627805a7c6", "研究活动/中东/非洲", "https://www.jiia.or.jp/region-middle_east_africa/", "政治"),
            ("2a05f45f-91e3-4e4d-9bd5-0866bba0ffbc", "研究活动/中国", "https://www.jiia.or.jp/region-china/", "政治"),
            ("0456959c-29d0-80c3-a5b5-32b60d83042e", "研究活动/俄罗斯", "", "政治"),
            ("6cee3e10-e9d9-4bfc-8979-fe04f89bbba4", "研究活动/俄罗斯/独联体", "https://www.jiia.or.jp/region-russia/", "政治"),
            ("113e7f89-2f1f-4f4c-8436-c8338ae9d0d1", "研究活动/印太", "https://www.jiia.or.jp/region-indo-pacific/", "政治"),
            ("9403cff0-b6b3-49a2-911d-dc7e312a9aa8", "研究活动/安全", "https://www.jiia.or.jp/topic-security/", "政治"),
            ("240e004d-87ee-414d-9a9a-0e3d9477e164", "研究活动/朝鲜半岛", "https://www.jiia.or.jp/region-korean_peninsula/", "政治"),
            ("6df40091-9b3d-4a4c-b7b4-f2903b0c45d8", "研究活动/欧洲", "https://www.jiia.or.jp/region-europe/", "政治"),
            ("424f6bb4-b658-4395-8e81-d535a5c473a4", "研究活动/经济与全球问题", "https://www.jiia.or.jp/topic-economy_global_issue/", "政治"),
            ("6d9bbc1f-c1c8-4c34-956c-254eb65bdf5a", "研究活动/美国", "https://www.jiia.or.jp/region-americas/", "政治"),
            ("6784f76f-cd34-a7a8-eecf-adc9d9790f02", "研究活动/裁军", "", "政治"),
            ("eadb7090-c277-4955-a885-bee8e3aa6d2c", "研究活动/裁军/科技", "https://www.jiia.or.jp/topic-cdast/archive.html", "政治"),
            ("0ae57d16-dada-4042-a960-1e378455058a", "研究活动/领土、主权、历史", "https://www.jiia.or.jp/jic/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//ul[@class="list-article"]/li//a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                url = urljoin(response.url, news_url)
                if "www.jiia.or.jp/column" not in url:
                    continue
                yield url

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:

        time_ = response.xpath('//dl[@class="txt-date"]/dt/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[contains(@class,"WordSection")]/*|//div[@class="detail-hero"]//img|'
                                   '')
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
                    if news_tag.root.tag == "figure":
                        con_img = self.parse_single_img(response, news_tag.xpath('./img'))
                        if con_img:
                            content.extend(con_img)
                        text_dict = self.parseOnetext(news_tag.xpath("./p"))
                        if text_dict:
                            content.extend(text_dict)

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
