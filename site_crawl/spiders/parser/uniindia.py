# -*- coding: utf-8 -*-
from datetime import datetime

from .base_parser import BaseParser


class UniIndiaParser(BaseParser):
    name = 'uniIndia'
    channel = [
        {
            "origin": "News",
            "tran": "news",
            "url": "https://www.uniindia.com/page/news"
        },
    ]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response):
        news_urls = response.xpath('//h2[@class="entry-title"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                if not news_url.__contains__('http'):
                    news_url = 'http://www.uniindia.com' + news_url
                yield news_url

    def get_title(self, response):
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="") or ""
        news_issue_title = title.strip()
        if not news_issue_title:
            news_issue_title = response.xpath('//meta[@property="og:description"]/@content').extract_first(
                default="").strip()
        return news_issue_title or ""

    def get_author(self, response):
        # author = response.xpath('//meta[@property="article:author"]/@content').extract_first(default="") or ""
        # news_issue_author = author.strip()
        return ''

    def get_pub_time(self, response):
        # Posted at: Apr 21 2021  3:15PM
        time_ = response.xpath('//span[@class="storydate"]/text()').extract_first() or ""
        if time_:
            news_issue_time = datetime.strptime(
                time_.replace("Posted at: ", "").replace("PM", "").replace("AM", "").strip(), "%b %d %Y  %H:%M")
            pub_time = self.get_timestamp_by_datetime(news_issue_time)
        else:
            pub_time = self.get_now_timestamp()
        return pub_time

    def get_content_media(self, response):

        content = []
        media_list_ = []
        news_tags = response.xpath('//span[@class="storydetails"] | '
                                   '//div[@class="storyImg"]/img|'
                                   '//div[@class="paragraph"]|'
                                   '//div[@class="row text-center"]/div[1]//div[@class="entry-header"]//img|'
                                   '//div[@class="paragraph"]/p')
        if news_tags:
            for news_tag in news_tags:
                dic = {}
                if not news_tag.root.tag == 'img':
                    con = news_tag.xpath('./text()').extract() or ""
                    con = [c.strip() for c in con]
                    con = ''.join([c for c in con if c != ""])
                    dic['content'] = con
                    dic['type'] = 'text'
                    content.append(dic)
                else:
                    img_url = news_tag.attrib.get('src')
                    if img_url:
                        if "default-image" in img_url:
                            img_url = news_tag.attrib.get("data-original")
                        img_dec = news_tag.attrib.get('alt')
                        img_name = self.get_md5_value(img_url) + '.jpg'
                        img_path = img_name
                        dic['content'] = img_path
                        dic['type'] = 'img'

                        media = dict()
                        media['media_type'] = 'img'
                        media['media_url'] = img_url
                        media['path'] = "OssPath" + img_path
                        media['alt'] = img_dec
                        media_list_.append(media)
                        content.append(dic)
        return content, media_list_
