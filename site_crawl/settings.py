BOT_NAME = 'site_crawl'
SPIDER_MODULES = ['site_crawl.spiders']
NEWSPIDER_MODULE = 'site_crawl.spiders'
ROBOTSTXT_OBEY = False

# scrapy-redis 配置
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
SCHEDULER_PERSIST = True  # 队列持久化
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
STATS_CLASS = "scrapy_redis.stats.RedisStatsCollector"
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.SpiderPriorityQueue'
# SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.FifoQueue'  # 先进先出队列

COOKIES_ENABLED = False
DOWNLOADER_MIDDLEWARES = {
    'site_crawl.middlewares.ProxyMiddleawre': 901,
    'site_crawl.middlewares.ReportRequestFailedMiddleware': 901,
}

DOWNLOAD_DELEY = 1
CONCURRENT_REQUESTS = 15
DOWNLOAD_TIME = 120

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 ' \
             'Safari/537.36 '

CHROME_TIMEOUT = 15
REDIS_HOST = '124.221.92.125'
REDIS_PORT = 63791

REDIS_SETTING = {
    "host": REDIS_HOST,
    "port": REDIS_PORT,
    "pwd": "",
    "pwd_param": {"pwd": ""},
    "news_key": 'BasicSpider:start_urls',
    "db": 0,
    "redis_news_queue": "news:src:Queue",
    "redis_comment_queue": "news:comment:url",
    "error_board_mag_queue": "news:board:error"
}
KAFKA_SETTING = {
    "KAFKA_SERVERS": '',
    "KAFKA_TOPIC": 'news-data'
}
PG_SETTING = {
    "Host": "xxx",
    "User": "postgres",
    "Db": "news",
    "PassWord": "abc123",
    "Port": 55433,
}
REDIS_START_URLS_BATCH_SIZE = 25
proxy = {
    "https": "http://127.0.0.1:9910",
    "http": "http://127.0.0.1:9910",
}

ITEM_PIPELINES = {
    'site_crawl.pipelines.KafkaPipeline': 300,
    # 'site_crawl.pipelines.NewsRedisPipeline': 301,
}
LOG_LEVEL = 'INFO'
# windows
MEMUSAGE_ENABLED = False
# 是否在开始之前清空 调度器和去重记录，True=清空，False=不清空
SCHEDULER_FLUSH_ON_START = True

EN_PROXY = True
