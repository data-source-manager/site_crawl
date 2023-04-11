# -*- coding: utf-8 -*-
import datetime
import json
import os
import traceback
from hashlib import md5

import langdetect
import scrapy
from scrapy_redis.spiders import RedisSpider

from apps.app import Apps
from apps.entry_id import source_dict
from service.log.log_deal import log_obj
from service.redisservice.redisservice import redisDeal
from site_crawl.items import LogItem, NewsItem


class BasicSpider(RedisSpider):
    name = 'BasicSpider'
    redis_key = "BasicSpider:start_urls"
    media_list = {}

    def __init__(self, *args, **kwargs):
        super(BasicSpider, self).__init__(*args, **kwargs)
        self.quit = False
        self.redis = redisDeal
        self.html_root_path = "/Users/hq/websitespider/site_crawl/html"

    def next_requests(self):
        """
        重写scrapy中start_url请求，使得原本该传入redis的为url，现在变成字典。
        """
        try:
            found = 0
            while found < self.redis_batch_size:
                data_raw = self.redis.rpop(self.redis_key)  # 从redis中取出内容
                if not data_raw:
                    break
                data = json.loads(data_raw)  # 存入redis的内容是json，需要转化
                if "url" not in data:
                    log_obj.deal_log(f'{self.redis_key} get a data not exist url! data: {data}', level='warn')
                    break

                # 找到某个插件，读取插件配置
                meta = data.get('meta')
                appid = meta.get('appid')
                if not appid:
                    msg = LogItem(code=1001, time=self.get_time(), msg=f"{meta}无appid")
                    log_obj.deal_log(f'{msg} no appid', level='warn')
                    continue
                app = Apps.get(appid)
                app_class = app.appclass()
                app_name = app.appname
                method = app_class.method

                meta['app_class'] = app_class
                meta['app_name'] = app_name
                meta['app_domain'] = app.appdomain
                meta['channel_url'] = data['url']
                meta['apppid'] = appid
                # 设置初始请求类型
                meta['method'] = method

                if method in ['get', 'post', 'selenium']:
                    # req = scrapy.Request(url=data['url'], meta=meta, dont_filter=True)  # 发出请求
                    req = self.deal_request(data['url'], meta, dont_filter=True)
                else:
                    req = None
                    log = LogItem(code=1007, time=self.get_time(), msg=f'{appid}-method set wrong!')
                    log_obj.deal_log(log)
                if req:
                    yield req
                    found += 1
                else:
                    log_obj.deal_log(f"Request not made from data: {data}", level='info')
            if found:
                log_obj.deal_log(f"Read {found} requests from '{self.redis_key}'", level='info')
        except Exception as e:
            log = LogItem(code=1001, time=self.get_time(), msg=traceback.format_exc())
            log_obj.deal_log(log)

    def parse(self, response, **kwargs):
        meta = response.meta
        app_class = meta['app_class']

        try:
            news_num = 0
            result = app_class.parse_list(response)
            for list_url in result:
                if type(list_url) == dict:
                    item = list_url["real_url"]
                    meta["origin_url"] = list_url["origin_url"]
                else:
                    item = list_url

                news_num += 1
                meta['real_url'] = item
                yield self.deal_request(item, meta, callback=self.parse_item)
            if news_num == 0:
                code = 1000
                msg = f'name: {meta["app_name"]}, url: {response.url}; Got url list is None!'
                log = LogItem(code=code, time=self.get_time(), msg=msg)
                log_obj.deal_log(log, level='warning')
        except GeneratorExit:
            pass
        except:
            self.redis.lpushErrorBoard({"site_board_uuid": meta.get("board_id"), "msg": traceback.format_exc()})

            code = 1002
            msg = 'Parse response fail - {}: {}'.format(meta["app_name"], traceback.format_exc())
            log = LogItem(code=code, time=self.get_time(), msg=msg)
            log_obj.deal_log(log)

    def parse_item(self, response):
        meta = response.meta
        app_class = response.meta['app_class']
        url = response.url
        if url.lower().endswith('.pdf'):
            url = response.meta['real_url']
        origin_url = meta.get('origin_url') if meta.get('origin_url') else url
        try:
            item = NewsItem(
                site_id=getattr(app_class, "site_id", "") if getattr(app_class, "site_id", "") else source_dict.get(
                    meta.get("source_name", "")),
                board_id=meta.get("board_id", ""),
                url=origin_url,
                channel=app_class.get_channel(response),
                title=app_class.get_title(response),
                contents=app_class.get_content_media(response),
                author=app_class.get_author(response),
                detected_lang=app_class.get_detected_lang(response),
                publish_time=app_class.get_pub_time(response),
                tags=app_class.get_tags(response),
                article_source=app_class.get_repost_source(response),
                if_repost=app_class.get_if_repost(response),
                like_count=app_class.get_like_count(response),
                comment_count=app_class.get_comment_count(response),
                forward_count=app_class.get_forward_count(response),
                read_count=app_class.get_read_count(response)
            )

            item["uuid"] = md5(
                (json.dumps(item.get("channel")) + item.get('title', '') + item.get('publish_time', '')).encode(
                    'utf-8')).hexdigest()
            yield item
        except:
            code = 1003
            msg = 'Parse item fail! name:{}, url:{}, error:{}'.format(response.meta["app_name"], response.url,
                                                                      traceback.format_exc())
            log = LogItem(code=code, time=self.get_time(), msg=msg)
            log_obj.deal_log(log)

    def deal_request(self, url, meta, dont_filter=False, callback=None):
        method = meta['method']
        headers = meta.get('headers') or None
        if method in ['get', 'selenium']:
            return scrapy.Request(url=url, meta=meta, headers=headers, callback=callback,
                                  dont_filter=dont_filter)  # 发出请求
        # post
        else:
            posturl = meta.get('posturl') or url
            postdata = meta.get('postdata') or None
            return scrapy.Request(posturl, headers=headers, body=postdata, method='POST', meta=meta, callback=callback,
                                  dont_filter=dont_filter)

    def get_time(self):
        return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

    def save_json(self, item):
        info_dict = {item['uuid']: {"url": item["url"], "channel": item["channel"]}}
        with open("spider_info.json", "a", encoding="utf-8") as f:
            f.write(json.dumps(info_dict) + "\n")

    def save_resp_html(self, lang: str, news_uuid: str, title: str, response):
        appid = response.meta.get("appid")
        if not lang:
            lang = langdetect.detect(f"{title}")

        save_path = os.path.join(self.html_root_path, "en")
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        html_path = os.path.join(save_path, f"{appid}_{news_uuid}.html")
        with open(html_path, "wb") as f:
            f.write(response.body)
