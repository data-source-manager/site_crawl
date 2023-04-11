import datetime
import json

from scrapy.utils.project import get_project_settings

from service.redisservice.redisservice import redisDeal
from util.site_deal.site_board import siteDeal

settings = get_project_settings()


class Master:
    """
    推送单个站点板块到redis
    """

    def __init__(self):
        self.redis = redisDeal
        self.channel = siteDeal

    def push_urls(self, siteId):
        single_site_boards = self.channel.get_single_site_board(siteId)
        for board in single_site_boards:
            i = 1
            self.redis.lpushNewBoard(json.dumps(board))  # 存入内容
            print('[{}] lpush {},推送进度{}/{},'.format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                board.get("url"), i, len(single_site_boards)))
            i += 1

        self.redis.close()


class MasterPlus:
    """
    推送所有爬取url到redis
    """

    def __init__(self):
        self.redis = redisDeal
        self.channel = siteDeal

    def push_site_url(self):
        all_site_boards = self.channel.get_all_site_boards()
        for board in all_site_boards:
            i = 1
            self.redis.lpushNewBoard(json.dumps(board))
            print('[{}] lpush {},推送进度{}/{},'.format(
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                board.get('meta').get("url"), i, len(all_site_boards)))

        self.redis.close()
