import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class TwVipParser(BaseParser):
    name = 'vip'
    # 站点id
    site_id = "5264a0c7-6766-454d-a821-e1030640a65b"
    # 站点名
    site_name = "联合报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "5264a0c7-6766-454d-a821-e1030640a65b", "source_name": "联合报", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("22c409d5-f709-4dc5-b63b-29ea0c77b79b", "专题", "https://vip.udn.com/vip/cate/121912?from=menu", "政治"),
            ("2683a712-ac3d-11ed-b5c8-1094bbebe6dc", "军武", "https://vip.udn.com/vip/cate/121915?from=menu", "政治"),
            ("6755f306-87aa-5a5b-ae51-c1bccf6657e1", "听幕后", "https://vip.udn.com/vip/cate/122044?from=menu", "政治"),
            ("36eaf312-ac3d-11ed-b57e-1094bbebe6dc", "听幕后/你给我记者", "https://vip.udn.com/vip/cate/122044/122045?from=vipudn_main2_cate", "政治"),
            ("294c3389-fc22-3858-831f-2ea18641716a", "听幕后/特辑", "https://vip.udn.com/vip/cate/122044/122741?from=vipudn_main2_cate", "政治"),
            ("538fb6e2-fb0e-42f9-9b46-2561888d8bbf", "听幕后/白话财经", "https://vip.udn.com/vip/cate/122044/122242?from=vipudn_main2_cate", "政治"),
            ("ed9a0b19-1e18-536f-b2f6-2c0e1d2c15b0", "听幕后/远方", "https://vip.udn.com/vip/cate/122044/122216?from=vipudn_main2_cate", "政治"),
            ("1d775678-11d4-3d42-9121-eef8cf4e2303", "听幕后/部队锅", "https://vip.udn.com/vip/cate/122044/122244?from=vipudn_main2_cate", "政治"),
            ("4784ceb4-ac3d-11ed-b950-1094bbebe6dc", "听幕后/郭崇伦会客堂", "https://vip.udn.com/vip/cate/122044/122217?from=vipudn_main2_cate", "政治"),
            ("a50db805-f033-3028-b05a-e34565ebde05", "国际", "https://vip.udn.com/vip/cate/121910?from=menu", "政治"),
            ("14e5765c-ac3d-11ed-9fdf-1094bbebe6dc", "政治", "https://vip.udn.com/vip/cate/121155?from=menu", "政治"),
            ("24b76e0c-9f7b-5b1b-bda8-fd0421feaf79", "教育", "https://vip.udn.com/vip/cate/122862?from=menu", "政治"),
            ("6f28d972-0263-3c8f-bf3d-5c177e103338", "生活", "https://vip.udn.com/vip/cate/121911?from=menu", "政治"),
            ("91058476-c706-41b4-81e2-dd41c20c2f04", "评论", "https://vip.udn.com/vip/cate/122364?from=menu", "政治"),
            ("8a5d22e0-7727-4321-bf50-18e0c2919489", "财经", "https://vip.udn.com/vip/cate/121909?from=menu", "政治"),
        ]
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h2[@class="story-list__title"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//h1[@class="article-content__title"]/text()').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//time[@class="article-content__time"]/text()').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//a[@class="tag"]/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip():
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath('//section[@class="article-content__editor"]/*|//img[@class=" ls-is-cached"]')
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
                    if news_tag.root.tag in ["h2", "h3", "h5", "span", "p"]:
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
