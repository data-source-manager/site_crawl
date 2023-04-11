import re
import time
from urllib.parse import urljoin

import requests
from scrapy import Selector

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class TwSetnParser(BaseParser):
    name = 'tw_setn'

    # 站点id
    site_id = "63b1513d-2821-431d-9765-4cdae966d581"
    # 站点名
    site_name = "三立新闻网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "63b1513d-2821-431d-9765-4cdae966d581", "source_name": "三立新闻网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f64fe534-86a4-3faa-a146-e1c929981ec7", "新闻总览", "", "政治"),
            ("72e34348-8ca7-11ed-a26d-1094bbebe6dc", "新闻总览/政治", "https://www.setn.com/ViewAll.aspx?PageGroupID=6", "政治"),
            ("81ca62ce-8ca7-11ed-9bd9-1094bbebe6dc", "新闻总览/两岸", "https://www.setn.com/ViewAll.aspx?PageGroupID=68", "政治"),
            ("ef5c4168-8ca7-11ed-8de2-1094bbebe6dc", "影音", "", "政治"),
            ("1b9fe112-8ca8-11ed-8816-1094bbebe6dc", "影音/政治", "https://www.setn.com/videos.aspx?PageGroupID=6", "政治"),
            ("24a00b5c-8ca8-11ed-bce2-1094bbebe6dc", "专题", "", "政治"),
            ("2f3993d0-8ca8-11ed-92d0-1094bbebe6dc", "专题/政治", "https://www.setn.com/Plist.aspx?PageGroupID=6", "政治"),
            ("374a294a-8ca8-11ed-9892-1094bbebe6dc", "专题/国际", "https://www.setn.com/Plist.aspx?PageGroupID=5", "政治"),
            ("fd29d440-518a-3dd8-b303-8aae38c01173", "团辑", "", "政治"),
            ("b8028d0f-f889-32bb-808e-50a65c1da766", "团辑/军事", "https://www.setn.com/photocatalog.aspx?ProjectType=10", "政治"),
            ("f643255a-84b8-325f-b9b1-bb02764b5002", "团辑/要闻", "https://www.setn.com/photocatalog.aspx?ProjectType=1", "政治"),
            ("c8965930-2eb6-3c80-a9ab-5bd8c805faf0", "名家", "", "政治"),
            ("13b935af-8528-31da-922a-c97a39157fe6", "名家/时事评论", "https://www.setn.com/Catalog_Column.aspx?SubCateID=35", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "63b1513d-2821-431d-9765-4cdae966d581"

    def parse_list(self, response) -> list:
        if "Plist" in response.url:
            url_lists = response.xpath('//div[contains(@class,"projectList")]/a/@href').extract() or ""
            if url_lists:
                for url_list in url_lists:
                    url = "https://www.setn.com/" + url_list
                    news_urls = Selector(text=requests.get(url).text).xpath(
                        '//div[@class="news-title"]//a/@href|//div[@class="newsimg-area-item-2 "]/a/@href').extract() or ""
                    if news_urls:
                        for news_url in list(set(news_urls)):
                            yield urljoin(response.url, news_url)
        elif "videos" in response.url:
            news_urls = response.xpath('//div[@class="col-lg-3 col-sm-6 openvod"]/@data-vodurl').extract() or ""
            url_template = 'https://www.setn.com/News.aspx?NewsID={}&utm_source=www.setn.com&utm_medium=setnvideo&utm_campaign=setnnews'
            if news_urls:
                for news_url in news_urls:
                    newid = re.findall('/VOD\.aspx\?IsVOD=true&newsid=(.*)&videoid', news_url)[0]
                    yield url_template.format(newid)
        else:
            news_urls = response.xpath('//h3[@class="view-li-title"]/a/@href|'
                                       '//div[@class="newsimg-area-item-3"]/a/@href|'
                                       '//div[@class="newsimg-area-item-2 "]/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="news-title-3"]/text()|'
                               '//div[@class="news-title"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:

        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@class="keyword page-keyword-area"]//a/strong/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//div[@id="Content1"]//img|//div[@id="Content1"]/*|//iframe[@class="vodFrame"]|'
                                   '//a[@data-target="#photo_view"]/img|//div[contains(@class,"photoGrid-item")]//img|'
                                   '//div[@id="Content1"]/p//a')
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
            oneCons = "".join(cons).strip().replace('\u3000', '').replace('\xa0', '')
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
