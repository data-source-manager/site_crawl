"""client entry"""
# -*- coding:utf-8 -*-
from scrapy import cmdline


if __name__ == "__main__":
    cmdline.execute(f"scrapy crawl BasicSpider".split())

