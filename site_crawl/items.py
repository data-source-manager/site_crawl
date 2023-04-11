import scrapy


class LogItem(scrapy.Item):
    code = scrapy.Field()  # 错误码
    time = scrapy.Field()  # 时间
    msg = scrapy.Field()  # 日志详情


class NewsItem(scrapy.Item):
    site_id = scrapy.Field()
    board_id = scrapy.Field()
    uuid = scrapy.Field()
    channel = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    contents = scrapy.Field()  # 新闻中的正文内容
    detected_lang = scrapy.Field()  # 新闻中识别的语言
    publish_time = scrapy.Field()  # 新闻发布时间
    crawl_time = scrapy.Field()  # 抓取时间
    # 可选字段
    subtitle = scrapy.Field()
    tags = scrapy.Field()  # 默认为空列表
    author = scrapy.Field()  # 作者字段为列表，需解析为精确的人名组织信息
    if_repost = scrapy.Field()
    article_source = scrapy.Field()

    # 可选计数器：赞评转阅
    like_count = scrapy.Field()  # 点赞数
    comment_count = scrapy.Field()  # 评论数
    forward_count = scrapy.Field()  # 转发数
    read_count = scrapy.Field()  # 阅读数
