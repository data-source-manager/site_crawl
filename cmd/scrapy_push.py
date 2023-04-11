import datetime
import traceback

from service.log.log_deal import log_obj
from service.push_urls import MasterPlus
from site_crawl.items import LogItem


def push_url():
    try:
        a = MasterPlus()
        a.push_site_url()
    except Exception as e:
        code = 1021
        msg = f'Project start master fail! --g-- Error: {traceback.format_exc()}'
        errorTime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        log = LogItem(code=code, time=errorTime, msg=msg)
        log_obj.deal_log(log)


if __name__ == '__main__':
    push_url()
