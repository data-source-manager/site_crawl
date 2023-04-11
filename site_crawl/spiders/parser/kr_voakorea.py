import time
from urllib.parse import urljoin

from service.reqservice.reqservice import get_response
from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

def get_media_url(url):
    all_media_urls = []
    proxy = {
        "https": "http://127.0.0.1:9910",
        "http": "http://127.0.0.1:9910",
    }
    selector = get_response(url)
    for t in selector.xpath('//div[@class="media-block__content"]/a/@href').extract()[1:3]:
        url = urljoin(url, t)
        all_media_urls.extend(get_response(url, proxy).xpath('//ul[@id="items"]/li/div/a/@href').extract())
    return all_media_urls


class KrVoakoreaParser(BaseParser):
    name = 'voakorea'
    
    # 站点id
    site_id = "f9e9126c-8903-4443-80f5-7a34fa3ef100"
    # 站点名
    site_name = "美国之音韩国版"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "f9e9126c-8903-4443-80f5-7a34fa3ef100", "source_name": "美国之音韩国版", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("f341bc7f-3964-a50b-f85b-d4ce6cb529d4", "美国之音韩国版_世界", "", "政治"),
            ("59de28e5-b0e6-46fe-bc08-6ef0af72cc98", "美国之音韩国版_世界/中东", "https://www.voakorea.com/z/2824", "政治"),
            ("5bcd3ee7-b9a3-4a79-9b9b-cfbf0076db99", "美国之音韩国版_世界/亚洲", "https://www.voakorea.com/z/2703", "政治"),
            ("222bcac2-a909-4114-899f-e228de901f68", "美国之音韩国版_世界/今日世界", "https://www.voakorea.com/z/2896", "政治"),
            ("7e5189be-98cc-4328-8a8d-7263a2892ec6", "美国之音韩国版_世界/今日美国", "https://www.voakorea.com/z/4705", "政治"),
            ("a228a014-b7cf-4d62-9e83-22cf4742cc98", "美国之音韩国版_世界/欧洲", "https://www.voakorea.com/z/2708", "政治"),
            ("412da0cd-fe2b-4812-9568-9255dc59d487", "美国之音韩国版_世界/美国", "https://www.voakorea.com/z/2700", "政治"),
            ("aeffdce1-2fa6-494d-8b04-fd5b5a760c08", "美国之音韩国版_世界/美洲与拉丁美洲", "https://www.voakorea.com/z/2826", "政治"),
            ("d9a6b55a-c2fd-46b8-a796-d37c0d912bc4", "美国之音韩国版_世界/赶上新闻", "https://www.voakorea.com/z/4706", "政治"),
            ("7bfb4462-f12c-4b67-9ad8-6986d70f3c87", "美国之音韩国版_世界/非洲", "https://www.voakorea.com/z/2699", "政治"),
            ("d58a0f19-16f5-4b8c-81da-1b3f539d4886", "美国之音韩国版_乌克兰", "https://www.voakorea.com/z/6936", "政治"),
            ("31ed5f1e-5f54-4440-b077-6873987e71ea", "美国之音韩国版_新的防疫危机", "https://www.voakorea.com/z/6495", "政治"),
            ("f7ccfecd-7e3c-f842-69af-037c13e3f57a", "美国之音韩国版_朝鲜半岛", "", "政治"),
            ("3c76ee6d-028c-4982-b74c-608cdd537111", "美国之音韩国版_朝鲜半岛/政治与安全", "https://www.voakorea.com/z/2767", "政治"),
            ("3d0a2597-10c1-4c67-b6ca-193c8360fc0a", "美国之音韩国版_朝鲜半岛/朝鲜叛逃者在美国的故事", "https://www.voakorea.com/z/4934", "政治"),
            ("af372c52-4f65-4980-ab26-7dc4d81ed0ac", "美国之音韩国版_朝鲜半岛/社会与人权", "https://www.voakorea.com/z/2769", "政治"),
            ("75648701-f4b0-460c-8259-6732b525481d", "美国之音韩国版_朝鲜半岛/经济与支持", "https://www.voakorea.com/z/2768", "政治"),
            ("4ac33d4f-df86-4dfb-b134-83280cc41ef1", "美国之音韩国版_电视", "https://www.voakorea.com/programs/tv", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "f9e9126c-8903-4443-80f5-7a34fa3ef100"

    def parse_list(self, response) -> list:
        if "programs/tv" in response.url:
            news_urls = get_media_url(response.url)
        else:
            news_urls = response.xpath(
                '//div[@id="content"]/div/div[@class="row"]//ul/li//div[@class="media-block "]/a/@href|'
                '//ul[@id="indexItems"]/li//div[@class="media-block"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@name="title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//meta[@name="Author"]/@content').extract()
        if authors:
            for au in authors:
                if au.strip():
                    author_list.append(au.strip())

        return author_list if author_list else []

    def get_pub_time(self, response) -> str:

        time_ = response.xpath('//span[@class="date"]/time/@datetime').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        con_set = set()

        news_tags = response.xpath('//div[@class="cover-media"]//div[@class="img-wrap"]//img|'
                                   '//div[@id="article-content"]/div/*|'
                                   '//div[@class="intro m-t-md"]/*|'
                                   '//a[@class="c-mmp__fallback-link"]')
        if news_tags:
            for news_tag in news_tags:
                if type(news_tag.root) == str:
                    con = news_tag.root.strip()
                    if con:
                        if con not in con_set:
                            con_set.add(con)
                            content.append({
                                "type": "text",
                                "data": con
                            })
                else:
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "div"]:
                        con_img = self.parse_single_img(response, news_tag.xpath('.//img'))
                        if con_img:
                            content.extend(con_img)
                        text_dict = self.parseOnetext(news_tag)
                        if text_dict:
                            if text_dict[0]["data"] not in con_set:
                                con_set.add(text_dict[0]["data"])
                                content.extend(text_dict)
                    if news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            con_text = self.parseOnetext(con)
                            if con_text:
                                if con_text[0]["data"] not in con_set:
                                    con_set.add(con_text[0]["data"])
                                    content.extend(con_text)
                    if news_tag.root.tag == "a":
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
        videoUrl = news_tag.xpath("./@href").extract_first()
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
