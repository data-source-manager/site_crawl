import redis
from scrapy.utils.project import get_project_settings

settings = get_project_settings()


class RedisC:
    def __init__(self):
        self.setting = settings["REDIS_SETTING"]
        self.redis_pool = redis.ConnectionPool(host=self.setting["host"],
                                               port=self.setting["port"],
                                               password=self.setting["pwd"],
                                               db=self.setting["db"]
                                               )
        self.redis_conn = redis.Redis(connection_pool=self.redis_pool)

    def lpushNewBoard(self, val: str):
        self.redis_conn.lpush(self.setting["news_key"], val)

    def lpushErrorBoard(self, val: str):
        self.redis_conn.lpush(self.setting["error_board_mag_queue"], val)

    def rpop(self, key) -> str:
        return self.redis_conn.rpop(key)

    def close(self):
        self.redis_conn.close()


redisDeal = RedisC()
