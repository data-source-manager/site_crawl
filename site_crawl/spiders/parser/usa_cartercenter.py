import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若详情url在网页中点击的和其真实数据不是同一个时
# 可以返回 {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class UsaCarterCenterParser(BaseParser):
    name = 'cartercenter'
    
    # 站点id
    site_id = "2e365eb1-3e91-b3a3-0bc8-d91dd076eb27"
    # 站点名
    site_name = "卡特中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "2e365eb1-3e91-b3a3-0bc8-d91dd076eb27", "source_name": "卡特中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("ae0d7209-e83d-3795-9f13-2b164f41a032", "新闻与事件", "", "政治"),
            ("4a8dc920-fe6f-11ec-a30b-d4619d029786", "新闻与事件/新闻稿", "https://www.cartercenter.org/news/pr/index.html", "政治"),
            ("4a8dca4c-fe6f-11ec-a30b-d4619d029786", "新闻与事件/演讲", "https://www.cartercenter.org/news/editorials_speeches/index.html", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        if "pr" in response.url:
            news_urls = response.xpath('//div[@class="articleListing"]')
            if news_urls:
                for news_url in news_urls:
                    rsp_url = news_url.xpath('./h3/a/@href').get()
                    rsp_time = news_url.xpath('./div/text()').get()
                    rsp_title = news_url.xpath('./h3/a/@title').get()
                    url = urljoin(response.url, rsp_url)
                    self.Dict[url] = {'time': rsp_time, 'title': rsp_title}
                    yield url
        else:
            news_urls = response.xpath('//div[@class="wysiwyg"]/p')
            if news_urls:
                for news_url in news_urls:
                    rsp_url = news_url.xpath('./a/@href').get()
                    rsp_time = news_url.xpath('.//strong[1]/text()').get()
                    rsp_title = news_url.xpath('./a/text()').get()
                    url = urljoin(response.url, rsp_url)
                    self.Dict[url] = {'time': rsp_time, 'title': rsp_title}
                    yield url

    def get_title(self, response) -> str:
        title = self.Dict[response.url]['title']
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        if ".pdf" in response.url:
            return []
        else:
            authors = response.xpath('//meta[@name="author"]/@content').extract()
            if authors:
                for au in authors:
                    if au.strip():
                        author_list.append(au.strip())

            return author_list if author_list else []

    def get_pub_time(self, response) -> str:

        time_ = self.Dict[response.url]['time']
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        if ".pdf" in response.url:
            return []
        else:
            tags = response.xpath('//div[@class="roundtable-other tags"]/a/text()').extract()
            if tags:
                for tag in tags:
                    if tag.strip():
                        tags_list.append(tag.strip())

            return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        if ".pdf" in response.url:
            file_dic = {
                "type": "file",
                "src": response.url,
                "name": None,
                "description": None,
                "md5src": self.get_md5_value(response.url) + ".pdf"
            }
            content.append(file_dic)
        else:
            news_tags = response.xpath('//div[@class="wysiwyg"]/*|//div[@class="wysiwyg"]/p/a|'
                                       '//div[@class="live-event-user"]/iframe|//div[@class="page-description"]/*|'
                                       '//div[@class="node__content"]//div[@class="field__item even"]//img|'
                                       '//div[@class="node__content"]//div[@class="field__item even"]/*|'
                                       '//div[@class="node__content"]//div[@class="field__item even"]/p/a|'
                                       '//div[@id="modal-ready"]/div/*|//div[@id="modal-ready"]/div/p/a|'
                                       '//div[@class="wysiwyg"]/div/*')
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
                        if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "a", "em"]:
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
                            con_file = self.parse_media(response, news_tag, media_type="mp4")
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
