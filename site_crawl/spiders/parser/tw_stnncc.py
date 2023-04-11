# -*- coding: utf-8 -*-
# update:(liyun|2023-03-09) -> 板块核对与解析代码覆盖
from datetime import datetime
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class TW_stnnccParser(BaseParser):
    name = 'tw_stnncc'

    
    # 站点id
    site_id = "fbae6e27-7cac-4dbd-840d-00da924d2009"
    # 站点名
    site_name = "星岛环球网"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "fbae6e27-7cac-4dbd-840d-00da924d2009", "source_name": "星岛环球网", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("c1950be0-5bd3-47c3-9b65-52135fbacf35", "内地", "https://www.stnn.cc/shizheng/", "政治"),
            ("19d88269-19f2-43b2-a758-1ed3a897431f", "内地/要闻", "https://www.stnn.cc/shizheng/ndyw/", "政治"),
            ("ae9e1cf0-f4fe-33e8-8188-625cb81860bf", "台湾", "https://www.stnn.cc/taiwan/", "政治"),
            ("4a8e8d42-fe6f-11ec-a30b-d4619d029786", "台湾/两岸原声", "https://www.stnn.cc/taiwan/strait/", "政治"),
            ("4a8e8900-fe6f-11ec-a30b-d4619d029786", "台湾/台湾新闻", "https://www.stnn.cc/taiwan/twnews/", "政治"),
            ("a3a55657-9967-4234-818d-5807d4c398df", "台湾/要闻", "https://news.stnn.cc/taiwan/twyw/", "政治"),
            ("906c3753-d720-3df5-b1a4-4d32e8a30c6b", "国际", "https://www.stnn.cc/guoji/", "政治"),
            ("4a8e9e86-fe6f-11ec-a30b-d4619d029786", "国际/军情", "https://www.stnn.cc/guoji/junqing/", "政治"),
            ("4a8e9fb2-fe6f-11ec-a30b-d4619d029786", "国际/国际新闻", "https://www.stnn.cc/guoji/world/", "政治"),
            ("4a8ea05c-fe6f-11ec-a30b-d4619d029786", "国际/海外媒体看中国", "https://www.stnn.cc/guoji/lookatchina/", "政治"),
            ("17976049-f58e-45b5-8087-4a20fb7646ad", "国际/要闻", "https://www.stnn.cc/guoji/gjyw/", "政治"),
            ("c53bc218-f870-3af7-b756-1dfc1397c0b2", "大中华", "", "政治"),
            ("4a8e96d4-fe6f-11ec-a30b-d4619d029786", "大中华/时评荟萃", "https://www.stnn.cc/shizheng/review/", "政治"),
            ("4a8e98fa-fe6f-11ec-a30b-d4619d029786", "大中华/星岛社论", "https://www.stnn.cc/shizheng/editorial/", "政治"),
            ("88873a9d-0624-4871-805d-f9107684db7d", "星岛大湾区", "https://www.stnn.cc/hk/", "政治"),
            ("fd82b660-117b-4b81-89ca-ada0d89d57b3", "星岛大湾区/珠三角新闻", "https://www.stnn.cc/hk/zsjxw/", "政治"),
            ("e8e2b7b5-337f-4c21-9adc-2da683ed2993", "星岛大湾区/香港要闻", "https://www.stnn.cc/hk/xgyw/", "政治"),
            ("22fb40e7-c41b-4faa-b7b9-479c561f35d3", "最新消息", "https://www.stnn.cc/kuaixun/", "政治"),
            ("0a6fb411-a4a3-3397-b724-55c68144aa16", "港澳", "", "政治"),
            ("4a8e91de-fe6f-11ec-a30b-d4619d029786", "港澳/澳门", "https://www.stnn.cc/gangao/aomen/", "政治"),
            ("4a8e956c-fe6f-11ec-a30b-d4619d029786", "港澳/评论", "https://www.stnn.cc/gangao/xjpl/", "政治"),
            ("4a8e906c-fe6f-11ec-a30b-d4619d029786", "港澳/香港", "https://www.stnn.cc/gangao/hongkong/", "政治"),
            ("c08b3c86-b8c6-475b-bddd-3e3d7c347095", "美国", "https://www.stnn.cc/usa/", "政治"),
            ("490c8402-7fed-41ee-97cd-77a3b0a1d173", "美国/要闻", "https://www.stnn.cc/usa/mgyw/", "政治"),
            ("b0c2235e-7218-11ed-a54c-d4619d029786", "评论", "https://www.stnn.cc/pinglun/", "政治"),
            ("8ce8915a-e9fa-4d5e-9a76-7fce641aebe7", "评论/星岛热评", "https://www.stnn.cc/pinglun/xdpl/", "政治"),
            ("8e5b9b49-3ec0-4577-a9bf-963e035c90c9", "评论/海外媒体看中国", "https://www.stnn.cc/pinglun/kzg/", "政治"),
            ("9b12b8fd-c17f-4e86-8043-9bdff1e17ec8", "评论/环球睿评", "https://www.stnn.cc/pinglun/hqrp/", "政治"),
            ("d6fc45f6-8f2c-4fa6-9e26-edc4501aaae3", "评论/评论", "https://www.stnn.cc/pinglun/pl/", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)
        self.Dict = {}

    def parse_list(self, response) -> list:
        url_filter = [data["url"] for data in TW_stnnccParser.channel]
        news_urls = response.xpath(
            '//div[@class="content-item-box"]//ul/li/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            news_url = urljoin(response.url, news_url)
            if news_url not in url_filter:
                yield news_url

    def get_title(self, response) -> str:
        return response.xpath(
            '//meta[@property="og:title"]/@content'
            '|//div[@class="ar_title"]/h2/text()'
            '|//div[@class="ar_title2"]/h2/text()'
        ).extract_first(default="").strip()

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath(
                '//div[@class="ar_title"]/div[1]/span/text()'
                '|//div[@class="ar_title2"]/div[1]/span/text()'
            ).extract_first(default="").strip()
            return datetime_helper.parseTimeWithOutTimeZone(datetime.strptime(publish_date, "%Y-%m-%d %H:%M"), site_name="星岛环球网")
        except:
            # import traceback
            # print(traceback.format_exc())
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@id="ar_font_set"]//p'
            '|//div[@id="ar_font_set"]//img'
            '|//source'
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
            # 解析视频
            elif tag.root.tag == "source":
                video_src = tag.attrib.get("src", "")
                if not video_src:
                    continue
                video_src = video_src.split("?")[0].split(" ")[0]
                video_src = urljoin(response.url, video_src)
                suffix = video_src.split(".")[-1].lower()
                if (not video_src.startswith('http')) or (suffix not in ["mp4"]):
                    continue
                content.append({
                    "type": "video",
                    "src": video_src,
                    "name": tag.attrib.get('alt', "").strip(),
                    "md5src": self.get_md5_value(video_src) + f'.mp4',
                    "description": "",
                })
            else:
                pass
        return content

    def get_detected_lang(self, response) -> str:
        return "zh_tw"

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
