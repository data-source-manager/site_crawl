import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class TwCnewsParser(BaseParser):
    name = 'cnews'
    
    # 站点id
    site_id = "9d4e3156-32d5-4a16-b5b9-241a337876bc"
    # 站点名
    site_name = "汇流新闻网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "9d4e3156-32d5-4a16-b5b9-241a337876bc", "source_name": "汇流新闻网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("7f09f6bf-9a75-36b0-8bf9-de6cf0b8c3e8", "国际汇流", "https://cnews.com.tw/category/%e5%9c%8b%e9%9a%9b%e5%8c%af%e6%b5%81/", "政治"),
            ("3c2a591c-6853-38eb-89c1-10f75d5e522a", "影音汇流", "https://cnews.com.tw/post_video/video/", "政治"),
            ("8260c7bf-6e70-3bf5-895b-5d791fdea17a", "政治汇流", "https://cnews.com.tw/category/%e6%94%bf%e6%b2%bb%e5%8c%af%e6%b5%81/page/1/", "政治"),
            ("19650622-95d3-3c48-9d7a-c58957d1d3a1", "新闻汇流", "https://cnews.com.tw/news/", "政治"),
            ("82f6c961-d9d1-5b9f-d9f7-89dd7f5e1521", "观点汇流", "https://cnews.com.tw/category/%e8%a7%80%e9%bb%9e%e5%8c%af%e6%b5%81/", "政治"),
            ("19414f6b-9ec0-3bcd-9a45-a0089c9525ee", "调查汇流", "https://cnews.com.tw/category/%e8%aa%bf%e6%9f%a5%e5%8c%af%e6%b5%81/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "0237b09f-8712-5605-c58e-408ded4bbfc2"

    def parse_list(self, response) -> list:
        if "video" in response.url:
            news_urls = response.xpath('//figure[@class="special-format"]/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)
        else:
            news_urls = response.xpath('//figure[@class="special-format"]/a/@href').extract() or ""
            if news_urls:
                for news_url in list(set(news_urls)):
                    yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//div[@class="_line"]/strong/text()').extract_first(default="")
        return title.strip().replace('\xa0', '') if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="twitter:data1"]/@content').extract()
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

        tags = response.xpath('//ul[@class="info"]/li[@class="tags"]/a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//article[contains(@id,"post")]/img|//article[contains(@id,"post")]/*|'
                                   '//div[@class="video-rwd"]/iframe')

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
