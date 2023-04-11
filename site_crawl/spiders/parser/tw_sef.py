import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


class TwSefParser(BaseParser):
    name = 'sef'
    
    # 站点id
    site_id = "b5309c26-0175-4ca6-a0e8-6d488ef85fcd"
    # 站点名
    site_name = "海基会"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "b5309c26-0175-4ca6-a0e8-6d488ef85fcd", "source_name": "海基会", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("cc3050c6-369d-9299-a348-9cbbad24139e", "主题专区", "", "政治"),
            ("fa5ad119-fa6d-4cb1-8a7f-6b65835020a4", "主题专区/两岸会谈", "https://www.sef.org.tw/category-1-23", "政治"),
            ("8d61f0c8-5972-47db-a5f9-b44b02110d2f", "主题专区/政策专区", "https://www.sef.org.tw/category-1-22", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "b5309c26-0175-4ca6-a0e8-6d488ef85fcd"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//section[@class="np"]//ul/li/a/@href|//div[@class="title"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            news_url = urljoin(response.url, news_url)
            if news_url.startswith('https://www.sef.org.tw/article'):
                yield news_url

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("-")[0].strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@name="DC.Date"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
                '//div[@id="center"]/div/section/div/*'
                '|//div[@class="pic"]//img'
        ) or []:
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = " ".join(tag.xpath(".//text()").extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            if tag.root.tag in ["ul", "ol"]:
                for con in tag.xpath('./li'):
                    con_text = self.parseOnetext(con)
                    con_text and content.extend(con_text)
            if tag.root.tag == "img":
                img_url = urljoin(response.url, tag.attrib.get("src", "").split("?")[0].strip())
                suffix = img_url.split(".")[-1].lower()
                if suffix not in ['jpg', 'png', 'jpeg']:
                    continue
                img_url and content.append({
                    "type": "image",
                    "src": img_url,
                    "md5src": self.get_md5_value(img_url) + f'.{suffix}',
                    "name": None,
                    "description": tag.attrib.get("alt", "").strip(),
                })
        # 资源下载(pdf)
        for tag in response.xpath('//div[@class="file_download"]//a'):
            file_url = tag.attrib.get('href', "")
            if not file_url.startswith('/files'):
                continue
            file_url = urljoin(response.url, file_url)
            content.append({
                "type": "file",
                "src": file_url,
                "name": tag.attrib.get('title', "").strip('(另開新視窗)').strip(),
                "description": None,
                "md5src": self.get_md5_value(file_url) + ".pdf"
            })
        # 特殊处理(会议记录类型页面)
        if not content:
            main_xpath = '//div[@id="center"]/div/section/section/dl'
            # 会议基本信息
            for tag in response.xpath(f'{main_xpath}/section[1]/span'):
                text = ": ".join([text.strip() for text in tag.xpath('.//text()').extract() if text.strip()]).strip()
                content.append({"data": text, "type": "text"})
            # 会议数据
            for tag in response.xpath(f'{main_xpath}/*'):
                if tag.root.tag == "dt":
                    text = "".join(tag.xpath(".//text()").extract()).strip()
                    text and content.append({"data": text, "type": "text"})
                elif tag.root.tag == "dd":
                    for text in tag.xpath(".//text()").extract():
                        text = text.strip()
                        text and content.append({"data": text, "type": "text"})
                else:
                    pass
        return content

    def get_detected_lang(self, response) -> str:
        return 'zh-CN'

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
