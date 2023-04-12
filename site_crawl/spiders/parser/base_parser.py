# -*- coding: utf-8 -*-
import datetime
import hashlib
import time

import pytz


class BaseParser:
    """
    解析方法基类,
    子类需要重写实现以下部分方法。
    """

    def __init__(self):
        # 默认请求为get || post/selenium
        self.method = 'get'  # 定义获取新闻列表时的请求方法，若与新闻数据请求不统一需要重新设置。
        self.headers = None
        self.postdata = None
        self.cookie: dict = {}
        # self.selenium = False

    def parse_list(self, response):
        pass

    def get_title(self, response):
        pass

    def get_author(self, response):
        pass

    def get_pub_time(self, response):
        pass

    def get_content(self, response):
        pass

    def get_detected_lang(self, response):
        pass

    def get_tags(self, response):
        pass

    def get_if_repost(self, response):
        pass

    def get_repost_source(self, response):
        pass

    def get_like_count(self, response):
        pass

    def get_comment_count(self, response):
        pass

    def get_forward_count(self, response):
        pass

    def get_read_count(self, response):
        pass
        # def get_media_list(self, response):

    #     pass

    def get_channel(self, response):
        channel = {
            'name': response.meta.get('name'),
            'direction': response.meta.get('country'),
            'source_name': response.meta.get('site_name'),
            'site_board_name': response.meta.get('board_name'),
            'domain': response.meta.get('app_domain')
        }
        return channel

    def get_md5_value(self, s: str):
        my_md5 = hashlib.md5()
        my_md5.update(s.encode('utf-8'))  # 得到MD5消息摘要
        my_md5_digest = my_md5.hexdigest()  # 以16进制返回消息摘要，32位
        return my_md5_digest

    @staticmethod
    def get_timestamp_by_datetime(dt: datetime.datetime, TIME_ZONE='Asia/Shanghai') -> int:
        # datetime转时间戳，默认时区上海时间
        try:
            tz = pytz.timezone(TIME_ZONE)
            t = tz.localize(dt)
            t = t.astimezone(pytz.utc)
            ts = (int(time.mktime(t.utctimetuple())) - time.timezone) * 1000
            return ts
        except Exception as e:
            raise e

    @staticmethod
    def get_now_timestamp():
        ts = int(time.time() * 1000)
        return ts
