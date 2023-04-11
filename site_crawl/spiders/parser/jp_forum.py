import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


class JpForumParser(BaseParser):
    name = 'forum'
    
    # 站点id
    site_id = "e3b15fe7-c29f-44ff-8ded-1ad16ed6bc82"
    # 站点名
    site_name = "查塔姆研究所"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "e3b15fe7-c29f-44ff-8ded-1ad16ed6bc82", "source_name": "查塔姆研究所", "direction": "jp", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("823b7fd5-adb8-4b61-96fb-a70c3ed2d716", "新闻", "https://www.t-i-forum.co.jp/visitors/news/", "政治"),
            ("82e06639-7701-4809-b30d-96cb16a8fbff", "消息", "https://www.t-i-forum.co.jp/organizer/news/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

        self.detail = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="p-news__detail"]/p/a')
        if news_urls:
            for news_url in list(set(news_urls)):
                url = urljoin(response.url, news_url.xpath("./@href").extract_first())
                if "www.t-i-forum.co.jp" not in url:
                    continue
                if url.endswith(".pdf"):
                    fake_url = f'http://httpbin.org/base64/video{time.time()}.pdf'
                    title = news_url.xpath('.//text()').extract_first()
                    self.detail[fake_url] = title
                    self.detail[fake_url] = url
                    yield {'origin_url': url, 'real_url': fake_url}

                yield url

    def get_title(self, response) -> str:
        if ".pdf" in response.url:
            return self.detail[response.url]
        title = response.xpath('//h1[@class="p-article-header"]/span/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:

        time_ = response.xpath('//p[@class="p-article-meta__pubdate"]/span/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        if ".pdf" in response.url:
            content.append({
                "type": "file",
                "src": self.detail[response.url],
                "name": "",
                "description": None,
                "md5src": self.get_md5_value(self.detail[response.url]) + ".pdf"
            })
        else:
            news_tags = response.xpath('//div[@class="wysiwyg"]//text()')
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
