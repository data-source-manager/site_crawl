"""client entry"""
import os

from scrapy import cmdline

# -*- coding:utf-8 -*-

"""
app_id:必填
detail_url:需要测试的具体详情url
board_name_list:需要测试的站点板块列表
detail_url与board_name_list只能填一个
"""

absPath = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

if __name__ == "__main__":
    app_id = "3044"
    detail_url = ""
    board_name_list = []
    cmdline.execute(f"scrapy crawl single_spider_test -a appid={app_id} -a detail_url={detail_url} -a board_list={board_name_list}".split())
