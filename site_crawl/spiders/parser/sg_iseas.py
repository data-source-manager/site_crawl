from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class SgIseasParser(BaseParser):
    name = 'iseas'
    
    # 站点id
    site_id = "7d78c20f-2b02-4bba-bd29-bdd72af8a140"
    # 站点名
    site_name = "新加坡东南亚研究院"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7d78c20f-2b02-4bba-bd29-bdd72af8a140", "source_name": "新加坡东南亚研究院", "direction": "sg", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("10536125-7537-4e6c-85ea-bb28c64f34ea", "东盟焦点", "https://www.iseas.edu.sg/category/articles-commentaries/aseanfocus/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.detail = {}

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@class="entry-summary"]')
        if news_urls:
            for news_url in list(set(news_urls)):
                url = urljoin(response.url, news_url.xpath("./a/@href").extract_first())
                self.detail[url] = {
                    "title": news_url.xpath("./preceding-sibling::div[1]/h2/text()").extract_first(),
                }
                yield url

    def get_title(self, response) -> str:
        return self.detail[response.url]["title"]

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        return [{
            "type": "file",
            "src": response.url,
            "name": "",
            "description": None,
            "md5src": self.get_md5_value(response.url) + ".pdf"
        }]

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
