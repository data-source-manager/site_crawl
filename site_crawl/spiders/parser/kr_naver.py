# -*- coding: utf-8 -*-
# update:[liyun:2023-01-14] -> 新增板块与解析代码
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.tools import check_img


class KR_naverParser(BaseParser):
    name = 'kr_naver'
    
    # 站点id
    site_id = "47d5b563-bac5-4af4-bb52-4518a334d09b"
    # 站点名
    site_name = "naver新闻"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "47d5b563-bac5-4af4-bb52-4518a334d09b", "source_name": "naver新闻", "direction": "kr", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("b0c1910e-2561-e9e2-8c64-732028218e6d", "世界", "", "政治"),
            ("4f571f4c-181d-49f6-a568-bab76845915a", "世界/世界通用", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=104&sid2=322", "其他"),
            ("ce0247a9-7d1a-37c5-558e-10337b0bcb36", "世界/中东", "", "政治"),
            ("ed9ba555-cbd6-4a30-b192-bb6046a8bdb7", "世界/中东/非洲", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=104&sid2=234", "其他"),
            ("592b9a3c-7b48-5a5d-569d-20de4b31d442", "世界/亚洲", "", "政治"),
            ("5ef04b77-deee-454b-854e-3638ba8d8a05", "世界/亚洲/澳大利亚", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=104&sid2=231", "其他"),
            ("4658613a-c246-47c1-a952-b2995b6fb707", "世界/欧洲", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=104&sid2=233", "其他"),
            ("1be4d3cc-5c28-882c-547c-d75576431065", "世界/美国", "", "政治"),
            ("e67ce8f4-711b-4c49-a827-487d33ed9a6e", "世界/美国/拉丁美洲", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=104&sid2=232", "其他"),
            ("4a8da1ca-fe6f-11ec-a30b-d4619d029786", "政治", "https://news.naver.com/main/main.naver?mode=LSD&mid=shm&sid1=100", "政治"),
            ("d27202c9-7e16-4cad-b3a0-13c77d77f1c8", "政治/北朝鲜", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=100&sid2=268", "政治"),
            ("7bc98713-8263-01db-8991-80679a91637e", "政治/国会", "", "政治"),
            ("433ba38c-3333-4046-8ba5-70ee6822043f", "政治/国会/政党", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=100&sid2=265", "政治"),
            ("499c372c-68ad-41f8-f2b5-5f43b88b1dd8", "政治/国防", "", "政治"),
            ("26bcbaef-c69c-4e02-9e1e-6cae0f2a40bb", "政治/国防/外交", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=100&sid2=267", "政治"),
            ("35076e6c-acaa-4f36-bec7-8b621fb4e6f4", "政治/总裁办公室", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=100&sid2=264", "政治"),
            ("39eceb24-51eb-434b-a53e-fe98353af11c", "政治/行政", "https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid1=100&sid2=266", "政治"),
            ("4a8da238-fe6f-11ec-a30b-d4619d029786", "看法", "https://news.naver.com/main/hotissue/sectionList.naver?mid=hot&sid1=&cid=1086252", "政治"),
            ("f52fcb7a-bf5c-f2e1-7ac5-b7a70bb9d0ff", "观点", "", "政治"),
            ("880f392f-6077-4ffe-9300-6cec6208b5d5", "观点/专栏", "https://news.naver.com/opinion/column", "政治"),
            ("90a1e989-5e16-4210-a168-699aa053d494", "观点/社论", "https://news.naver.com/opinion/editorial", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="list_body newsflash_body"]/ul/li/dl/dt[1]/a/@href'
            '|//ul[@class="opinion_editorial_list _content_list"]/li/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        _time = response.xpath(
            '//span[@class="media_end_head_info_datestamp_time _ARTICLE_DATE_TIME"]/@data-date-time').extract_first(
            default="").strip()
        return _time if _time else "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:

        content = []
        for tag in response.xpath(
                '//div[@id="dic_area"]//img'
                '|//div[@id="newsct_article"]//iframe'
                '|//div[@id="dic_area"]//text()'
        ):
            # 解析文本
            if type(tag.root) == str:
                text = tag.root.strip()
                text and content.append({"data": text, "type": "text"})
            # 解析图像
            elif tag.root.tag == "img":
                img_url = tag.attrib.get("src", "").split("?")[0] or tag.attrib.get("data-src", "").split("?")[0]
                suffix = img_url.split(".")[-1].lower()
                if suffix not in ["jpg", "png", "jpeg"]:
                    continue
                content.append({
                    "type": "image",
                    "name": "",
                    "md5src": self.get_md5_value(img_url) + f'.{suffix}',
                    "description": "",
                    "src": img_url
                })
            # 解析视频
            elif tag.root.tag == "iframe":
                video_url = tag.attrib.get("data-src").strip()
                if not video_url:
                    continue
                content.append({
                    "type": "video",
                    "src": video_url,
                    "name": "",
                    "description": None,
                    "md5src": self.get_md5_value(video_url) + ".mp4"
                })
            else:
                pass
        return content

        # news_tags = response.xpath('//div[@id="dic_area"]/*|//div[@id="dic_area"]/text()')
        # if news_tags:
        #     for news_tag in news_tags:
        #         if type(news_tag.root) == str:
        #             con_text = news_tag.root
        #             if con_text.strip():
        #                 content.append({
        #                     "type": "text",
        #                     "data": con_text.strip()
        #                 })
        #         else:
        #             if news_tag.root.tag in ["h2", "h3", "h5", "span", "p", "em", "font", "div", "strong"]:
        #                 con_img = self.parse_img(response, news_tag)
        #                 if con_img:
        #                     content.extend(con_img)
        #                 text_dict = self.parseOnetext(news_tag)
        #                 if text_dict:
        #                     content.extend(text_dict)
        # return content

    def get_detected_lang(self, response) -> str:
        return "zh-cn"

    def parse_single_img(self, response, news_tag):
        img_list = []

        img_src = news_tag.xpath("./@data-src").extract_first()
        if check_img(img_src):
            img_url = urljoin(response.url, img_src)
            des = "".join(news_tag.xpath('.//em//text()').extract()).strip()
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

    def parse_text(self, news_tag):
        cons = news_tag.xpath('').extract() or ""

        new_cons = []

        if cons:
            for con in cons:
                if con.strip():
                    new_cons.append({'data': "".join(con).strip(), 'type': "text"})
        return new_cons

    def parseOnetext(self, news_tag) -> list:
        """"
            一个标签下不分段
        """
        cons = news_tag.xpath(".//text()").extract() or ""
        new_cons = []
        if cons:
            dic = {}
            oneCons = "".join(cons).strip().replace('\t', '').replace('\n', '')
            if oneCons:
                dic['data'] = oneCons
                dic['type'] = 'text'
                new_cons.append(dic)
        return new_cons

    def parse_img(self, response, news_tag):
        """
            先判断链接是否存在
        """
        imgs = news_tag.xpath('.//img')

        img_list = []

        if imgs:
            for img in imgs:
                img_src = img.xpath("./@data-src").extract_first()
                if img_src:
                    img_url = urljoin(response.url, img_src)

                    des = "".join(news_tag.xpath('.//em//text()').extract()).strip()
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
