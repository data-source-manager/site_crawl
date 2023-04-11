from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class MnDnnParser(BaseParser):
    name = 'dnn'
    
    # 站点id
    site_id = "daa8ca91-3557-4f3a-b9d5-9c32e3da9a04"
    # 站点名
    site_name = "蒙古日报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "daa8ca91-3557-4f3a-b9d5-9c32e3da9a04", "source_name": "蒙古日报", "direction": "mn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块主题)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("c3dcbb4f-8e8f-4a6c-9fc0-2219b7e548bb", "政治", "https://dnn.mn/%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D/%D1%83%D0%BB%D1%81-%D1%82%D3%A9%D1%80/", "政治"),
            ("6df3b527-175c-451a-99d2-76e463b5452f", "外国", "https://dnn.mn/%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D/%D0%B3%D0%B0%D0%B4%D0%B0%D0%B0%D0%B4/", "政治"),
            ("073329cd-bf76-4789-b486-440a44853ed5", "视频", "https://dnn.mn/%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE-%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D/", "政治"),
            ("c7f0b433-629d-77b7-e0ec-60bfbc03e41b", "角落", "", "政治"),
            ("c329f522-97a6-42fa-91a1-11d9302505e6", "角落/科学与技术", "https://dnn.mn/%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D/%D0%B1%D1%83%D0%BB%D0%B0%D0%BD%D0%B3%D1%83%D1%83%D0%B4/%D1%88%D0%B8%D0%BD%D0%B6%D0%BB%D1%8D%D1%85-%D1%83%D1%85%D0%B0%D0%B0%D0%BD-%D1%82%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8/", "政治"),
        ]
    ]


    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = 'daa8ca91-3557-4f3a-b9d5-9c32e3da9a04'

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//ul[@class="article-list"]/li/h4/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//article//h1/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//div[@class="article_publish"]/span/text()').extract_first()
        if time_:
            time_ = datetime.strptime(time_, "%Y.%m.%d %H:%M")
            return datetime_helper.parseTimeWithOutTimeZone(time_, site_name="日报")

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//meta[@name="keywords"]/@content').extract()
        if tags:
            if "," in tags:
                tags = tags[0].split(",")
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="el_content page_main"]/h2/img|'
                                   '//div[@class="el_content page_main"]/div/*|'
                                   '//div[@class="el_content page_main"]/*')
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
                        con_img = self.parse_single_img(response, news_tag.xpath(".//img"))
                        if con_img:
                            content.extend(con_img)
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
