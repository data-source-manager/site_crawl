# Name: 站点解析器开发
# Date: 2023-03-16
# Author: liyun
# Desc: None


import datetime
import re
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser


class MnMMinfoParser(BaseParser):
    name = 'mn_mminfo'
    
    # 站点id
    site_id = "38b8d1d0-390b-4060-88ce-46fddc346ea2"
    # 站点名
    site_name = "MMINFO"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "38b8d1d0-390b-4060-88ce-46fddc346ea2", "source_name": "MMINFO", "direction": "mn", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("12ad4698-ef7b-4147-87d2-bc75aec82061", "世界", "http://www.mminfo.mn/categories/view/5", "政治"),
            ("d33b2256-330c-415d-8fa9-961fd631be8b", "图片新闻", "http://www.mminfo.mn/tags/view/18", "政治"),
            ("36cdeef1-4d07-4a49-8955-95170d6934ea", "政治", "http://www.mminfo.mn/politics/home", "政治"),
            ("28d1939e-4b70-4e64-b151-d88eeb244d45", "政治/常务委员会", "http://www.mminfo.mn/politics/tags/14", "政治"),
            ("bb1b5ca3-5276-4186-b51b-20ff19df05b3", "政治/总统", "http://www.mminfo.mn/politics/tags/11", "政治"),
            ("b0c17a93-5094-43ef-90fb-24dbf53c87a2", "政治/政府", "http://www.mminfo.mn/politics/tags/17", "政治"),
            ("de867a86-6295-4b68-8535-b33f6c4629c0", "政治/文章", "http://www.mminfo.mn/politics/tags/20", "政治"),
            ("bb226438-637e-4922-a7a1-a3ced778a435", "政治/派对", "http://www.mminfo.mn/politics/tags/32", "政治"),
            ("a6708ff6-6273-447a-80da-b30560a2fe88", "政治/选举", "http://www.mminfo.mn/politics/tags/1", "政治"),
            ("b486367b-cd10-4aec-9669-cbba8842bf9f", "政治/面试", "http://www.mminfo.mn/politics/tags/22", "政治"),
            ("97d4c1d1-1cf4-4c12-9f30-33a1b2c942e9", "观点", "http://www.mminfo.mn/categories/view/7", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "38b8d1d0-390b-4060-88ce-46fddc346ea2"

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="news"]/a/@href'
            '|//article//h4/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//span[@class="a"]/a/text()').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//span[@class="d"]/text()').extract_first(default="").strip()
            if "цагийн өмнө" in publish_date:
                h = re.search(r"\d+", publish_date).group()
                publish_date = str(datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(hours=-int(h)))
            elif "өдрийн өмнө" in publish_date:
                d = re.search(r"\d+", publish_date).group()
                publish_date = str(datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(days=-int(d)))
            else:
                publish_date = str(datetime.datetime.strptime(publish_date, "%Y-%m-%d"))
            return publish_date
        except:
            import traceback
            print(traceback.format_exc())
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="ft"]/*'
            '|//div[@class="ft"]/blockquote/p'
            '|//div[@id="ch1"]/img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
            # 解析图像数据
            elif tag.root.tag == "img":
                img_src = tag.attrib.get("srcset", "") or tag.attrib.get("src", "")
                if not img_src:
                    continue
                img_src = img_src.split("?")[0].split(" ")[0]
                img_src = urljoin(response.url, img_src)
                suffix = img_src.split(".")[-1].lower()
                if (not img_src.startswith('http')) or (suffix not in ["jpg", 'png', 'jpeg']):
                    continue
                content.append({
                    "type": "image",
                    "src": img_src,
                    "name": tag.attrib.get('alt', "").strip(),
                    "md5src": self.get_md5_value(img_src) + f'.{suffix}',
                    "description": tag.xpath("../figcaption/text()").extract_first(default="").strip(),
                })
            else:
                pass
        return content

    def get_detected_lang(self, response) -> str:
        return "en"

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
