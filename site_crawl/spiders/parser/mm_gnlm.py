import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


class MMGnlmParser(BaseParser):
    name = 'gnlm'
    
    # 站点id
    site_id = "943659f7-893b-4369-ad9a-009af093b683"
    # 站点名
    site_name = "缅甸新光报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "943659f7-893b-4369-ad9a-009af093b683", "source_name": "缅甸新光报", "direction": "mm", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("76b9c07d-90b0-4c7d-9685-ec912d36c356", "世界", "", "政治"),
            ("629ed447-bfcd-4091-8348-54b9ce0d0d17", "世界/亚洲", "https://www.gnlm.com.mm/category/world/asia/", "其他"),
            ("b53f0f9b-e6b2-4f73-a0ef-92cf15e8aa1c", "世界/经济", "https://www.gnlm.com.mm/category/world/economic/", "经济"),
            ("62b65645-e95f-483e-bfd0-765dba2972fa", "全国的", "", "政治"),
            ("170c4473-4839-45b7-a373-26a8573a1846", "全国的/国家行政委员会主席", "https://www.gnlm.com.mm/category/national/commander-in-chief-of-defence-services/", "政治"),
            ("544ee708-cc1d-4f5e-86ac-5f90b5364443", "全国的/部门", "https://www.gnlm.com.mm/category/national/ministry/", "政治"),
            ("e181b1e0-929e-4fd4-97d2-81a2ebba8661", "公告", "https://www.gnlm.com.mm/category/announcement/", "政治"),
            ("c227afa7-1f51-4da2-af17-335d0a2f2792", "商业", "https://www.gnlm.com.mm/category/business/", "政治"),
            ("a7317816-112c-4103-824b-0352cff92c45", "商业/政策", "https://www.gnlm.com.mm/category/business/policy/", "经济"),
            ("51c137ce-71d0-4627-b53e-d2bae4fd74f8", "商业/营销", "https://www.gnlm.com.mm/category/business/marketing/", "经济"),
            ("c197a5bb-7496-433c-9040-787a09adfacd", "国际", "https://www.gnlm.com.mm/category/national/", "政治"),
            ("4a8d9478-fe6f-11ec-a30b-d4619d029786", "本地新闻", "https://www.gnlm.com.mm/category/local-news/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.site_id = "943659f7-893b-4369-ad9a-009af093b683"

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h4[@class="post-title"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="entry-title"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        author_list = []

        authors = response.xpath('//li[@class="post-author"]/a/@title').extract()
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
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 正文p标签数
        content_p_tag_num = len(response.xpath('//div[@class="entry-content mt-2"]/p').extract())
        news_tags = response.xpath(
            '//div[contains(@class,"entry-content")]/*'
            '|//div[@class="entry-content mt-2"]/p/noscript/img'
            '|//div[@id="content"]//article/noscript/img')
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
                    if news_tag.root.tag in ["h4", "h3", "h5", "span", "p"]:
                        # 根据正文p标签数判断是否需要对p标签内的文本进行聚合
                        if content_p_tag_num > 1:
                            texts = " ".join(news_tag.xpath(".//text()").extract() or []).strip()
                            texts and content.append({"data": texts, "type": "text"})
                        else:
                            texts = self.parse_text(news_tag)
                            texts and content.extend(texts)
                    elif news_tag.root.tag == "ol" or news_tag.root.tag == "ul":
                        for con in news_tag.xpath('./li'):
                            con_text = self.parseOnetext(con)
                            if con_text:
                                content.extend(con_text)
                    elif news_tag.root.tag == "img":
                        con_img = self.parse_single_img(response, news_tag)
                        if con_img:
                            content.extend(con_img)
        # 解析文件
        for url in response.xpath('//div[@class="entry-content mt-2"]/p/a/@href').extract():
            if url.lower().endswith(".pdf"):
                content.append({
                    "type": "file",
                    "src": url,
                    "name": "",
                    "description": None,
                    "md5src": self.get_md5_value(url) + f'.{url.split(".")[-1]}'
                })
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
                des = "".join(news_tag.xpath(".//img/@alt").extract())

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
        return response.xpath('//li[@class="post-count"]/span/text()').extract_first()

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
