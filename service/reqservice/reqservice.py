import traceback

import requests
from scrapy import Selector

from service.log.log_deal import log_obj
from site_crawl.items import LogItem
from util.tools import get_time


def get_response(url: str, proxy=""):
    try:
        res = requests.get(url, proxies=proxy)
        return Selector(text=res.text)
    except:
        msg = f"get response failed, error:{traceback.format_exc()}"
        log = LogItem(code=3000, time=get_time(), msg=msg)
        log_obj.deal_log(log)
