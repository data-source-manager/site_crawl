import ast
import datetime
import json
import re
import traceback
from hashlib import md5

import scrapy

from apps.app import Apps
from service.log.log_deal import log_obj
from site_crawl.items import NewsItem


def get_time():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')


def init_channel(channel: list, spec_board: list) -> list:
    """
    channel:站点的板块列表
    spec_board:指定的板块列表名
    """
    new_channel = []
    for d in channel:
        if d["site_board_name"] in spec_board:
            new_channel.append(d)

    return new_channel


class SiteTestSpiderSpider(scrapy.Spider):
    name = 'single_spider_test'

    media_list = {}

    def start_requests(self):
        if len(self.appid) >= 1:
            app_class = Apps.get(int(self.appid)).appclass()
            if len(self.detail_url) > 4:
                yield scrapy.Request(url=self.detail_url, callback=self.parse, meta={
                    "app_class": app_class
                })
            else:
                # 指定测试的板块
                specify_board = ast.literal_eval(self.board_list)
                if specify_board:
                    site_boards = init_channel(app_class.channel, specify_board)
                else:
                    site_boards = app_class.channel
                start_url = [x for x in site_boards]
                if start_url:
                    for url in start_url:
                        yield scrapy.Request(url=url["url"], callback=self.parse_list, meta={
                            "app_class": app_class
                        })
                else:
                    log = f'The start_url list is None'
                    log_obj.deal_log(log, level="warn")
        else:
            log = f'appid is None'
            log_obj.deal_log(log, level="error")

    def parse_list(self, response):
        print("=============开始解析列表url===========")
        meta = response.meta
        article_url = meta["app_class"].parse_list(response)
        if article_url:
            for x in article_url:
                yield scrapy.Request(x, callback=self.parse, meta={
                    "app_class": meta["app_class"]
                })
        else:
            log = f'文章列表为空'
            log_obj.deal_log(log, level="error")

    def parse(self, response, **kwargs):
        print("=============开始解析详情url===========")
        meta = response.meta
        try:
            item = NewsItem(
                url=response.url,
                channel="",
                title=meta["app_class"].get_title(response),
                contents=meta["app_class"].get_content_media(response),
                author=meta["app_class"].get_author(response),
                detected_lang=meta["app_class"].get_detected_lang(response),
                publish_time=meta["app_class"].get_pub_time(response),
                tags=meta["app_class"].get_tags(response),
                repost_source=meta["app_class"].get_repost_source(response),
                if_repost=meta["app_class"].get_if_repost(response),
                like_count=meta["app_class"].get_like_count(response),
                comment_count=meta["app_class"].get_comment_count(response),
                forward_count=meta["app_class"].get_forward_count(response),
                read_count=meta["app_class"].get_read_count(response)
            )

            item["uuid"] = md5(
                (json.dumps(item.get("channel")) + item.get('title', '') + item.get('publish_time', '')).encode(
                    'utf-8')).hexdigest()
            if re.findall('"type": "video",', json.dumps(item["contents"],ensure_ascii=False)) or\
                    re.findall('"type": "audio",', json.dumps(item["contents"],ensure_ascii=False)):
                self.media_list[item["url"]] = item["contents"]
            yield item
        except Exception as e:
            log = f'文章解析失败,url:{response.url},error_msg:{traceback.format_exc()}'
            log_obj.deal_log(log, level="error")
