# -*- coding: utf-8 -*-
# update:(liyun|2023-03-14) -> 板块核对与解析代码覆盖
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser
from util.time_deal import datetime_helper


class USA_stimsonParser(BaseParser):
    name = 'usa_stimson'

    
    # 站点id
    site_id = "853caaf7-dcb7-42ce-90fc-920e297befb5"
    # 站点名
    site_name = "史汀生研究中心"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "853caaf7-dcb7-42ce-90fc-920e297befb5", "source_name": "史汀生研究中心", "direction": "usa", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("e9976742-8c0a-e497-55d5-852efb83c0f8", "事件", "https://www.stimson.org/events/", "政治"),
            ("f8a38394-9ccb-e7ef-a7ce-0d807048e528", "关键地点", "", "政治"),
            ("50bac654-5826-b0b6-2915-1e29e3c81fb1", "关键地点/东南亚", "https://www.stimson.org/research/pivotal-places/asia-indopac/southeast-asia/", "政治"),
            ("ef5bd9f0-d510-9220-e08f-22bc7aff7fb8", "关键地点/中东和北非", "https://www.stimson.org/research/pivotal-places/mena/", "政治"),
            ("f2ab9965-286f-a38c-9bc9-babe7ab17658", "关键地点/中国", "https://www.stimson.org/research/pivotal-places/asia-indopac/china/", "政治"),
            ("09d91a60-e33a-7efb-86bd-2c45ad164484", "关键地点/亚洲和印太地区", "https://www.stimson.org/research/pivotal-places/asia-indopac/", "政治"),
            ("346e2641-41b7-71a5-5577-859c7810eb40", "关键地点/俄罗斯", "https://www.stimson.org/research/pivotal-places/russia/", "政治"),
            ("8572595a-443f-26c1-7feb-c0fac2196453", "关键地点/南亚", "https://www.stimson.org/research/pivotal-places/asia-indopac/south-asia/", "政治"),
            ("cc89de65-b55d-1e52-c15b-2e21b0c62ee1", "关键地点/日本", "https://www.stimson.org/research/pivotal-places/asia-indopac/japan/", "政治"),
            ("c99f0af4-09fe-fa0a-9228-c6d4cd60913a", "关键地点/朝鲜半岛", "https://www.stimson.org/research/pivotal-places/asia-indopac/korean-peninsula/", "政治"),
            ("4a8db9ee-fe6f-11ec-a30b-d4619d029786", "媒体", "https://www.stimson.org/media-announcements/", "政治"),
            ("c087d75d-08ab-22f2-ec2a-75e021592c23", "安全与策略", "", "政治"),
            ("3bd5b364-b7a1-199e-066a-2d1aef79272a", "安全与策略/国防政策与态势", "https://www.stimson.org/research/security-strategy/defense-policy-posture/", "政治"),
            ("0724eced-5c1c-8c87-faef-93fa3979443f", "安全与策略/外交与对话", "https://www.stimson.org/research/security-strategy/diplomacy-dialogue/", "政治"),
            ("0cd631ea-d77d-1ddb-58c3-6d0656ab2df1", "安全与策略/大战略", "https://www.stimson.org/research/security-strategy/grand-strategy/", "政治"),
            ("c72658bd-bfcc-2813-3fde-4305dbd04071", "新闻与公告", "https://www.stimson.org/about/stimson/media-announcements/", "政治"),
            ("4a8db4c6-fe6f-11ec-a30b-d4619d029786", "活动", "https://www.stimson.org/?event-status=past", "政治"),
            ("b487d0ce-63fa-3b39-b2d9-913b19948c54", "研究", "", "政治"),
            ("4a8db868-fe6f-11ec-a30b-d4619d029786", "研究/亚洲", "https://www.stimson.org/asia/", "政治"),
            ("4a8db778-fe6f-11ec-a30b-d4619d029786", "研究/国际秩序与冲突", "https://www.stimson.org/international-order/", "政治"),
            ("4a8db52a-fe6f-11ec-a30b-d4619d029786", "研究/科技与贸易", "https://www.stimson.org/tech-trade/", "政治"),
            ("4a8db958-fe6f-11ec-a30b-d4619d029786", "研究/美国外交政策", "https://www.stimson.org/us-foreign-policy/", "政治"),
            ("4a8db638-fe6f-11ec-a30b-d4619d029786", "研究/资源与气候", "https://www.stimson.org/resources-climate/", "政治"),
            ("6cc254eb-3108-fa97-12b6-a4ca4b755cfd", "贸易与技术", "", "政治"),
            ("1b736d3f-6558-c550-b4c9-09cb797e357a", "贸易与技术/常规武器", "https://www.stimson.org/research/trade-tech/conventional-arms/", "军事"),
            ("b9b16add-352c-ca79-e905-f9e36d75760f", "贸易与技术/新兴技术", "https://www.stimson.org/research/trade-tech/emerging-tech/", "军事"),
            ("6bab3c05-d0ff-4c90-ba9d-74d5ec9b3d47", "贸易与技术/贸易风险缓解", "https://www.stimson.org/research/trade-tech/trade-risk/", "军事"),
            ("3f871fb5-004b-8a88-5f29-9779d9e0a2c0", "贸易与技术/防扩散", "https://www.stimson.org/research/trade-tech/nonproliferation/", "军事"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response) -> list:
        news_urls = response.xpath(
            '//div[@class="elementor-widget-container"]/a/@href'
            '|//h2[@class="entry-title"]/a/@href'
        ).extract() or []
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        return response.xpath('//meta[@property="og:title"]/@content').extract_first(default="").split("•")[0].strip()

    def get_author(self, response) -> list:
        return [a.strip() for a in response.xpath('//div[contains(@class, "wpv-view-layout")]/div/a/text()').extract() or []]

    def get_pub_time(self, response) -> str:
        try:
            publish_date = response.xpath('//meta[@property="article:modified_time"]/@content').extract_first(default="").strip()
            publish_date = datetime_helper.parseTimeWithTimeZone(publish_date)
            return publish_date
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        content = []
        # 解析正文数据
        for tag in response.xpath(
            '//div[@class="elementor-widget-container"]/p'
            '|//div[@class="elementor-widget-container"]/img'
            '|//iframe[@class="elementor-video"]'
            '|//video'
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
            elif tag.root.tag == "iframe":
                video_src = tag.attrib.get("src", "")
                if not video_src.startswith("https://www.youtube.com/"):
                    continue
                content.append({
                    "type": "video",
                    "src": video_src,
                    "name": tag.attrib.get('alt', "").strip(),
                    "md5src": self.get_md5_value(video_src) + f'.mp4',
                    "description": "",
                })
            elif tag.root.tag == "video":
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
        return "zh"

    def get_like_count(self, response) -> int:
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        read_count = 0
        return read_count

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
