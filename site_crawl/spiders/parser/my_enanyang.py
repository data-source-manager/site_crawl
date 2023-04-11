import time
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper
from util.tools import check_img


# 若文章的详情数据网页展示url和数据真实存在url
# ['real_url'] 会被请求,最后的item.url = item["origin_url"]
# 可以返回 yield {'origin_url': real_url,'real_url': fake_url}这样一个字典,origin_url是网页中的url，real_url为数据所在的url

class MyEnanyangParser(BaseParser):
    name = 'enanyang'
    
    # 站点id
    site_id = "7023fef0-e409-4847-903b-afa97da961c2"
    # 站点名
    site_name = "马来西亚南洋商报"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "7023fef0-e409-4847-903b-afa97da961c2", "source_name": "马来西亚南洋商报", "direction": "my", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("9db1765d-ef9f-4dc7-95b1-0b289e2a4572", "全球大抗疫", "https://www.enanyang.my/%E5%85%A8%E7%90%83%E5%A4%A7%E6%8A%97%E7%96%AB-0", "政治"),
            ("4a8d0b3e-fe6f-11ec-a30b-d4619d029786", "国际", "", "政治"),
            ("cb9f81f2-3f7c-4ee3-9363-7e61c3836b10", "国际/东盟+", "https://www.enanyang.my/%E5%9B%BD%E9%99%85/%E4%B8%9C%E7%9B%9F", "政治"),
            ("7bfdf657-aac7-43a7-9ddc-21278bc8d3f5", "国际/亚洲周刊专区", "https://www.enanyang.my/%E5%9B%BD%E9%99%85/%E4%BA%9A%E6%B4%B2%E5%91%A8%E5%88%8A%E4%B8%93%E5%8C%BA", "政治"),
            ("84573029-5eab-4b85-9d3b-16f9060bcaec", "国际/大千", "https://www.enanyang.my/%E5%9B%BD%E9%99%85/%E5%A4%A7%E5%8D%83", "政治"),
            ("be649914-daf3-484c-b2cf-9d27311d184b", "国际/德国之声", "https://www.enanyang.my/%E5%9B%BD%E9%99%85/%E5%BE%B7%E5%9B%BD%E4%B9%8B%E5%A3%B0", "政治"),
            ("48e059ea-65b2-dfc4-2071-9c464235b908", "时事", "", "政治"),
            ("f6d1fd77-6cf3-4755-aceb-0adf1bb934cb", "时事/商团", "https://www.enanyang.my/%E6%97%B6%E4%BA%8B/%E5%95%86%E5%9B%A2", "政治"),
            ("731da731-00b6-4d2e-9bce-9a87c8819227", "时事/政治", "https://www.enanyang.my/%E6%97%B6%E4%BA%8B/%E6%94%BF%E6%B2%BB", "政治"),
            ("3aaed071-fb2f-41cd-94b7-f4726c723a8b", "时事/文教", "https://www.enanyang.my/%E6%97%B6%E4%BA%8B/%E6%96%87%E6%95%99", "政治"),
            ("493226ec-86cf-4fd4-b91a-d3d45c70b9de", "时事/要闻", "https://www.enanyang.my/%E6%97%B6%E4%BA%8B/%E8%A6%81%E9%97%BB", "政治"),
            ("4a8d0b70-fe6f-11ec-a30b-d4619d029786", "财经", "", "政治"),
            ("8aceca45-62ce-415c-948c-ebcdd5a548d4", "财经/BFM财经", "https://www.enanyang.my/%E8%B4%A2%E7%BB%8F/bfm%E8%B4%A2%E4%BB%8A", "政治"),
            ("63686b67-a314-4ae5-be40-cecf6dff9a85", "财经/国际财经", "https://www.enanyang.my/%E8%B4%A2%E7%BB%8F/%E5%9B%BD%E9%99%85%E8%B4%A2%E7%BB%8F", "政治"),
            ("3430a6f3-1efc-429c-8ab2-fce75a48225c", "财经/财经新闻", "https://www.enanyang.my/%E8%B4%A2%E7%BB%8F/%E8%B4%A2%E7%BB%8F%E6%96%B0%E9%97%BB", "政治"),
            ("5e1f1fbd-956d-4a13-9c34-a6ad098f2329", "财经/财经最热Now", "https://www.enanyang.my/%E8%B4%A2%E7%BB%8F/%E8%B4%A2%E7%BB%8F%E6%9C%80%E7%83%ADnow", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//h2[@class="ttr_post_title"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="")
        return title.strip() if title else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_ = response.xpath('//meta[@property="article:published_time"]/@content').extract_first()
        if time_:
            pub_time = datetime_helper.fuzzy_parse_timestamp(time_)
            return str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pub_time)))

        return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        tags_list = []

        tags = response.xpath('//div[@id="main-content"]/div[@class="node-article-tags"]//a/text()').extract()
        if tags:
            for tag in tags:
                if tag.strip() and tag.strip() not in tags_list:
                    tags_list.append(tag.strip())

        return tags_list if tags_list else []

    def get_content_media(self, response) -> list:
        content = []

        news_tags = response.xpath(
            '//div[@class="node-article-paragraphs"]/div[1]//div[contains(@class,"paragraph--type--text")]/*|'
            '//div[@class="node-article-paragraphs"]/div[1]//div[contains(@class,"paragraph--type--image")]//img')
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
