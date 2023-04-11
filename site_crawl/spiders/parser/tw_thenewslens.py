import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TwThenewslensParser(BaseParser):
    name = 'thenewslens'
    
    # 站点id
    site_id = "5f5c84ee-3c19-46e1-9b57-5bbe16908841"
    # 站点名
    site_name = "关键评论"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "5f5c84ee-3c19-46e1-9b57-5bbe16908841", "source_name": "关键评论", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("226a6464-8876-3ec4-8252-75fc29050cb7", "全球与区域", "", "政治"),
            ("89809592-ba82-419d-9638-94411be59ff4", "全球与区域/中国", "https://www.thenewslens.com/category/china", "其他"),
            ("4a8cccfa-fe6f-11ec-a30b-d4619d029786", "全球与区域/国际", "https://www.thenewslens.com/category/world", "其他"),
            ("c108c52f-f8eb-3992-b0a2-fe5d88507bcb", "政治与政策", "", "政治"),
            ("4a8ccc5a-fe6f-11ec-a30b-d4619d029786", "政治与政策/军事", "https://www.thenewslens.com/category/military", "军事"),
            ("4a8ccbb0-fe6f-11ec-a30b-d4619d029786", "政治与政策/政治", "https://www.thenewslens.com/category/politics", "政治"),
            ("ce38e72d-ef36-cab2-e038-24b24804619b", "社会与公众", "", "政治"),
            ("aa1e3d03-5cd1-45b9-b20f-36b101d50aa3", "社会与公众/社会", "https://www.thenewslens.com/category/society", "其他"),
            ("f8aa1ca7-b069-8ab7-47d2-dd7fad98dacc", "财经与商业", "", "政治"),
            ("7c207c92-afbf-4966-904b-589e4406d3fd", "财经与商业/经济", "https://www.thenewslens.com/category/economy", "经济"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id='5f5c84ee-3c19-46e1-9b57-5bbe16908841'
    def parse_list(self, response) -> list:
        news_urls = response.xpath('//div[@id="list-container"]//h2[@class="title"]/a/@href').extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("-")[0].strip()

    def get_author(self, response) -> list:
        authors = response.xpath('//h3[@class="author-name"]/a/text()').extract()
        return [a.strip() for a in authors]

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))
        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags = response.xpath('//ul[@class="tags"]/a/@title|//h3[@class="tags"]/ul/li/a/@title').extract() or []
        return [t.strip() for t in tags]

    def get_content_media(self, response) -> list:
        content = []

        # 提取图像
        def extract_img(tag):
            if not tag:
                return None
            img_src = tag.attrib.get("srcset", "") or tag.attrib.get("src", "")
            img_src = img_src.split("?")[0].split(" ")[0]
            suffix = img_src.split(".")[-1].lower()
            if (not img_src.startswith('http')) or (suffix not in ["jpg", 'png', 'jpeg']):
                return None
            return {
                "type": "image",
                "src": img_src,
                "name": tag.attrib.get('alt', "").strip(),
                "md5src": self.get_md5_value(img_src) + f'.{suffix}',
                "description": None,
            }

        # (特殊处理)提取正文前置图像
        try:
            img_field = extract_img(list(response.xpath('//div[@class="article-header-container"]//img'))[0])
            img_field and content.append(img_field)
        except:
            pass
        # 解析正文数据
        for tag in response.xpath(
                '//article[@data-ad2trk-observe="Main Article"]/div/section/*'
                '|//article[@data-ad2trk-observe="Main Article"]/div/section//img'
                '|//div[@id="tnl-feature-article-content-section"]/div/img'
        ) or []:
            # 解析段落文本
            if tag.root.tag in ["p", "span", "h2", "h3", "h4"]:
                text = ' '.join(tag.xpath(".//text()").extract() or []).strip()
                # 正文结束中断解析
                if tag.root.tag == "h3" and text == "延伸閱讀":
                    break
                text and content.append({"data": text, "type": "text"})
            elif tag.root.tag in ["ul", "ol"]:
                for text in tag.xpath('./li//text()').extract() or []:
                    text = text.strip()
                    text and content.append({"data": text, "type": "text"})
            # 解析图像数据
            elif tag.root.tag == "img":
                img_field = extract_img(tag)
                img_field and content.append(img_field)
            else:
                pass
        return content

    def get_detected_lang(self, response) -> str:
        return "zh"

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
