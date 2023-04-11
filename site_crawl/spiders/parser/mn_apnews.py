from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class MnApnewsParser(BaseParser):
    name = 'apnews'
    channel = [
        {'url': 'https://apnews.com/hub/us-news?utm_source=apnewsnav&utm_medium=navigation', 'direction': 'mn',
         'source_name': '美联社新闻', 'site_board_name': '美国新闻', 'board_theme': '政治',
         'if_front_position': False, 'board_id': '52697b84-e092-4460-a8da-5cd9e1818de6'},
        {'url': 'https://apnews.com/hub/world-news?utm_source=apnewsnav&utm_medium=navigation',
         'direction': 'mn', 'source_name': '美联社新闻', 'site_board_name': '世界新闻', 'board_theme': '政治',
         'if_front_position': False, 'board_id': '1fd35ddd-363c-485b-9f1f-df618ccfb501'},
        {'url': 'https://apnews.com/hub/politics?utm_source=apnewsnav&utm_medium=navigation', 'direction': 'mn',
         'source_name': '美联社新闻', 'site_board_name': '政治', 'board_theme': '政治',
         'if_front_position': False, 'board_id': '9650d2a3-9876-45a7-ab2a-471d788926fb'},
        {'url': 'https://apnews.com/hub/business?utm_source=apnewsnav&utm_medium=navigation', 'direction': 'mn',
         'source_name': '美联社新闻', 'site_board_name': '商业', 'board_theme': '政治',
         'if_front_position': False, 'board_id': 'cae1dbce-1330-4407-b70e-bae9c4dccc60'},
        {'url': 'https://apnews.com/hub/technology?utm_source=apnewsnav&utm_medium=navigation',
         'direction': 'mn', 'source_name': '美联社新闻', 'site_board_name': '技术', 'board_theme': '政治',
         'if_front_position': False, 'board_id': '94b73ef4-eafb-4990-b190-033365eda320'},
        {'url': 'https://apnews.com/hub/science?utm_source=apnewsnav&utm_medium=navigation', 'direction': 'mn',
         'source_name': '美联社新闻', 'site_board_name': '科学', 'board_theme': '政治',
         'if_front_position': False, 'board_id': '533f9292-3453-42cd-a86e-6e75187a5c0e'}
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@data-key="card-headline"]/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="twitter:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            return datetime_helper.parseTimeWithTimeZone(time_)

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//video|//div[@class="Article"]/*|//a[@data-key="media-placeholder"]/img|'
                                   '//article[contains(@class,"article")]/p')
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
                    if news_tag.root.tag == "video":
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
