import json
import os

from loguru import logger

from service.pgservice.save_log_msg import mysqlDeal
from site_crawl.items import LogItem
from site_crawl.settings import MEMUSAGE_ENABLED

absPath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
logPath = os.path.join(absPath,  "_Log/spider.log")

if __name__ == '__main__':
    print(absPath)
    print(logPath)


class LogDeal:
    def __init__(self):
        logger.add(logPath, format="[{time:YYYY-MM-DD HH:mm:ss:SSS}] [{level}]: {message}", rotation='5 MB',
                   retention="7 days")
        self._logger = logger.bind()
        if MEMUSAGE_ENABLED:
            self.logPipeline = mysqlDeal

    def deal_log(self, log, level='error'):
        if isinstance(log, LogItem):
            if MEMUSAGE_ENABLED:
                self.logPipeline.insertLogs(dict(log))
            if level == 'error':
                self._logger.error(json.dumps(dict(log), ensure_ascii=False))
            elif level == 'info':
                self._logger.info(json.dumps(dict(log), ensure_ascii=False))
            elif level == 'warning' or level == 'warn':
                self._logger.warning(json.dumps(dict(log), ensure_ascii=False))
            else:
                self._logger.debug(json.dumps(dict(log), ensure_ascii=False))
        else:
            if level == 'error':
                self._logger.error(log)
            elif level == 'info':
                self._logger.info(log)
            elif level == 'warning' or level == 'warn':
                self._logger.warning(log)
            else:
                self._logger.debug(log)


log_obj = LogDeal()
