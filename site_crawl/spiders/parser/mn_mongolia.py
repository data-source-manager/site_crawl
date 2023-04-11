from urllib.parse import urljoin

import requests
from jsonpath import jsonpath

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class MnMongoliaParser(BaseParser):
    name = 'mongolia'
    channel = [
        {'url': 'https://mongolia.gogo.mn/i/7073', 'direction': 'mn', 'source_name': 'GoGo蒙古',
         'site_board_name': '政治', 'board_theme': '政治', 'if_front_position': False,
         'board_id': '7abcfbed-eb42-4a74-a050-651f78b9b619'},
        {'url': 'https://mongolia.gogo.mn/i/7068', 'direction': 'mn', 'source_name': 'GoGo蒙古',
         'site_board_name': '经济', 'board_theme': '政治', 'if_front_position': False,
         'board_id': '5dc942ed-e60e-4a14-9c7b-9eb1feb75624'},
        {'url': 'https://mongolia.gogo.mn/i/7368', 'direction': 'mn', 'source_name': 'GoGo蒙古',
         'site_board_name': '社会', 'board_theme': '政治', 'if_front_position': False,
         'board_id': '8a99e3a2-3e62-4045-b247-a959e4ab5db4'},
        {'url': 'https://mongolia.gogo.mn/i/7370', 'direction': 'mn', 'source_name': 'GoGo蒙古',
         'site_board_name': '面试', 'board_theme': '政治', 'if_front_position': False,
         'board_id': '20bdcd45-3ec0-41fd-9d77-011fdcbc3026'},
        {'url': 'https://mongolia.gogo.mn/i/7371', 'direction': 'mn', 'source_name': 'GoGo蒙古',
         'site_board_name': '文化', 'board_theme': '政治', 'if_front_position': False,
         'board_id': 'a2b4c17b-c3f8-48cc-bc09-d4af0bf061b1'}
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = []
        news_url_s = response.xpath('//meta[@property="og:url"]/@content').extract() or ""
        for u in news_url_s:
            news_url_ = u + "/fetch?"
            header = {
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
            }
            res = requests.get(news_url_, headers=header)
            html_date = res.json()
            lid = jsonpath(html_date, "$..lid")
            for i in lid:
                rsp_url = "https://mongolia.gogo.mn/r/" + i
                if rsp_url:
                    news_urls.append(rsp_url)
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@name="last-modified"]/@content').extract_first()
        if time_:
            return datetime_helper.parseTimeWithTimeZone(time_)

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@class="uk-margin-bottom"]//img|'
                                   '//div[contains(@class,"seo-bagana-tablet")]/p/text()')
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
