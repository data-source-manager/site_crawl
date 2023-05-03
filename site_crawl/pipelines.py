import datetime
import json
import logging
import os
import time
import traceback
from urllib.parse import unquote

import psycopg2
import redis
from kafka import KafkaProducer
from scrapy.utils.project import get_project_settings

from service.log.log_deal import log_obj
from site_crawl.items import LogItem, NewsItem
from util.time_deal.datetime_helper import fuzzy_parse_timestamp
from util.tools import get_time, getImage, getDomain

settings = get_project_settings()


class NewsRedisPipeline:
    def __init__(self):
        redis_ip = settings['REDIS_HOST']
        redis_port = settings['REDIS_PORT']
        redis_password = settings['REDIS_PASSWORD']
        redis_pool = redis.ConnectionPool(host=redis_ip, port=redis_port, password=redis_password, db=1)
        self.redis_conn = redis.Redis(connection_pool=redis_pool)
        self.comment_domain = ["www.chosun.com", "tw.news.yahoo.com", "newtalk.tw", "www.appledaily.com.tw",
                               "chinese.joins.com", "www.rti.org.tw"]

    def batchPush(self, redisKey, jsonList: list):
        with self.redis_conn.pipeline(transaction=False) as p:
            for xjson in jsonList:
                p.lpush(redisKey, json.dumps(xjson, ensure_ascii=False))
            p.execute()

    def pushComment(self, redisKey, value):
        if isinstance(value, str):
            self.redis_conn.lpush(redisKey, value)

    def process_item(self, item, spider):
        self.batchPush(settings["REDIS_QUEUE"], getImage(item))
        if getDomain(item['url']) in self.comment_domain:
            commentDict = {
                "comment_url": "",
                "failed_msg": ""
            }
            self.pushComment(settings['REDIS_COMMENT_QUEUE'], json.dumps(commentDict, ensure_ascii=False))


# 线下数据转csv测试
class ToJsonPipeline:
    def process_item(self, item, spider):
        file_path = os.path.abspath(os.path.join(os.path.abspath(__file__), "../"))
        json_file = os.path.join(file_path, "data_pkg/{}.json".format(item['channel']['domain']))
        if isinstance(item, NewsItem):
            personJsonInfo = self.genJson(item)
            with open(json_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(personJsonInfo, ensure_ascii=False))
                f.write('\n')
                print(personJsonInfo)
                print('save one jsondata')

    def genJson(self, item):
        return {
            "crawl_time": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            "url": item["url"],
            "title": item["title"].strip() if item.get("title") else "",
            "contents": item["contents"],
            "detected_lang": item["detected_lang"],
            "publish_time": item["publish_time"],
            "tags": item["tags"],
            "author": item["author"],
            "if_repost": item["if_repost"],
            "like_count": item["like_count"],
            "comment_count": item["comment_count"],
            "forward_count": item["forward_count"],
            "read_count": item["read_count"],
            "repost_source": item['repost_source']
        }


# 字段检测管道
class checkItemFieldPipeline:
    def process_item(self, item, spider):
        if isinstance(item, NewsItem):
            if item["publish_time"] != "9999-01-01 00:00:00":
                if fuzzy_parse_timestamp(item["publish_time"]) > int(datetime.datetime.now().timestamp()):
                    log_obj.deal_log(log=f"the publish time is bigger than current time :url:{item['url']}",
                                     level="error")
            if not item["title"]:
                log_obj.deal_log(log=f"title lose :url:{item['url']}", level="error")
            if not item["contents"]:
                log_obj.deal_log(log=f"content lose :url:{item['url']}", level="warn")
            if item["contents"]:
                for con in item["contents"]:
                    if con["type"]:
                        if con["type"] == "image":
                            if "data:image" in con["src"] or not con["src"].startswith("http"):
                                log_obj.deal_log(
                                    log=f"image url error :articl_url:{item['url']},img_url:{con['src']}",
                                    level="error")
                        if con["type"] == "file":
                            if not con["src"].startswith("http"):
                                log_obj.deal_log(log=f"file without http :url:{item['url']}", level="error")
                    else:
                        log_obj.deal_log(log=f"{con}无type类型,url:{item['url']}", level="error")
            print(item)
            return item

    def close_spider(self, spider):
        """
        多媒体的检测太过耗时
        """
        pass


class KafkaPipeline(object):
    def __init__(self, servers, topic):
        self.producer = KafkaProducer(bootstrap_servers=servers, api_version=(0, 10, 2))
        self.topic = topic

    @classmethod
    def from_crawler(cls, crawler):
        kf_setting = crawler.settings.get('KAFKA_SETTING')
        servers = kf_setting.get("KAFKA_SERVERS")
        topic = kf_setting.get('KAFKA_TOPIC')
        return cls(servers, topic)

    def close_spider(self, spider):
        self.producer.close()

    def process_item(self, item, spider):
        print(item)
        data = json.dumps(dict(item), ensure_ascii=False).encode('utf-8')
        self.producer.send(self.topic, data)
        return item


class site_crawlPgPipeline:
    def __init__(self):
        self.setting = settings["PG_SETTING"]
        self.con = psycopg2.connect(host=self.setting["Host"],
                                    user=self.setting["User"],
                                    password=self.setting["PassWord"],
                                    database=self.setting["Db"],
                                    port=self.setting['Port']
                                    )

        self.cursor = self.con.cursor()

    def close_spider(self):
        self.con.close()

    def process_item(self, item, spider):
        if isinstance(item, NewsItem):
            logging.info(item)
            try:
                title = item['title'].replace('&nbsp;', ' ').replace('\xa0', '').replace('\u3000', ' ').strip()
                content = json.dumps(item["contents"], ensure_ascii=False)
                if item["contents"]:
                    module = item["channel"]
                    data = (
                        item["uuid"],
                        title,
                        content,
                        module["domain"],
                        module["source_name"],
                        unquote(item["url"]),
                        json.dumps(item["author"], ensure_ascii=False),
                        item["comment_count"],
                        item["read_count"],
                        item["like_count"],
                        item["forward_count"],
                        "",
                        item["detected_lang"],
                        module["direction"],
                        json.dumps(item["tags"], ensure_ascii=False),
                        module["site_board_name"],
                        item["board_id"],
                        item["article_source"],
                        item["publish_time"],
                        get_time(),
                        item["site_id"]
                    )
                    insert_sql = f'insert INTO article (news_uuid, title, content, site_domain, source_name, url, author, comment_count, read_count,' \
                                 f' like_count, forward_count, site_type, lang, direction, article_tag, site_board_name, ' \
                                 f'site_board_uuid, repost_source, publish_time, insert_time, site_uuid)VALUES {data}'
                    print(insert_sql)
                    self.cursor.execute(insert_sql)
                    self.con.commit()
                else:
                    msg = 'content is empty please check it,id:{},domain:{}'.format(item["url"],
                                                                                    item["channel"]["domain"])
                    log = LogItem(code=1010, time=get_time(), msg=msg)
                    log_obj.deal_log(log)
            except:
                self.cursor.execute("ROLLBACK")
                msg = 'Parse pipelineItem fail: error:{},item:{}'.format(traceback.format_exc(), item)
                log = LogItem(code=1004, time=get_time(), msg=msg)
                log_obj.deal_log(log)
        return item
