# -*- coding: utf-8 -*-
import datetime
import re

from dateutil.relativedelta import relativedelta

from site_crawl.spiders.parser.base_parser import BaseParser


class TassParser(BaseParser):
    name = 'tass'
    channel = [
        {
            "origin": "v-strane",
            "tran": "v-strane",
            "url": "https://tass.ru/v-strane",
            "headers": {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
                'cookie': '__jhash_=941; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F99.0.4844.82%20Safari%2F537.36; __js_p_=390,1800,0,0; __hash_=1878ca7370aa9d0a2b7227afa2b737eb; tass_uuid=EAA53176-407D-415F-82C3-610B3E7BAC45',
            }
        },
        {
            "origin": "politika",
            "tran": "politika",
            "url": "https://tass.ru/politika",
            "headers": {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
                'cookie': '__jhash_=941; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F99.0.4844.82%20Safari%2F537.36; __js_p_=390,1800,0,0; __hash_=1878ca7370aa9d0a2b7227afa2b737eb; tass_uuid=EAA53176-407D-415F-82C3-610B3E7BAC45',
            }
        },
        {
            "origin": "nacionalnye",
            "tran": "nacionalnye",
            "url": "https://tass.ru/nacionalnye-proekty",
            "headers": {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
                'cookie': '__jhash_=941; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F99.0.4844.82%20Safari%2F537.36; __js_p_=390,1800,0,0; __hash_=1878ca7370aa9d0a2b7227afa2b737eb; tass_uuid=EAA53176-407D-415F-82C3-610B3E7BAC45',
            }
        },
        {
            "origin": "panorama",
            "tran": "panorama",
            "url": "https://tass.ru/mezhdunarodnaya-panorama",
            "headers": {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
                'cookie': '__jhash_=941; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F99.0.4844.82%20Safari%2F537.36; __js_p_=390,1800,0,0; __hash_=1878ca7370aa9d0a2b7227afa2b737eb; tass_uuid=EAA53176-407D-415F-82C3-610B3E7BAC45',
            }
        },
        {
            "origin": "armiya",
            "tran": "armiya",
            "url": "https://tass.ru/armiya-i-opk",
            "headers": {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
                'cookie': '__jhash_=941; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F99.0.4844.82%20Safari%2F537.36; __js_p_=390,1800,0,0; __hash_=1878ca7370aa9d0a2b7227afa2b737eb; tass_uuid=EAA53176-407D-415F-82C3-610B3E7BAC45',
            }
        },
        {
            "origin": "obschestvo",
            "tran": "obschestvo",
            "url": "https://tass.ru/obschestvo",
            "headers": {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
                'cookie': '__jhash_=941; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F99.0.4844.82%20Safari%2F537.36; __js_p_=390,1800,0,0; __hash_=1878ca7370aa9d0a2b7227afa2b737eb; tass_uuid=EAA53176-407D-415F-82C3-610B3E7BAC45',
            }
        },
        {
            "origin": "proisshestviya",
            "tran": "proisshestviya",
            "url": "https://tass.ru/proisshestviya",
            "headerss": {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
                'cookie': '__jhash_=941; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F99.0.4844.82%20Safari%2F537.36; __js_p_=390,1800,0,0; __hash_=1878ca7370aa9d0a2b7227afa2b737eb; tass_uuid=EAA53176-407D-415F-82C3-610B3E7BAC45',
            }
        },
        {
            "origin": "ural-news",
            "tran": "ural-news",
            "url": "https://tass.ru/ural-news",
            "headers": {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36',
                'cookie': '__jhash_=941; __jua_=Mozilla%2F5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F99.0.4844.82%20Safari%2F537.36; __js_p_=390,1800,0,0; __hash_=1878ca7370aa9d0a2b7227afa2b737eb; tass_uuid=EAA53176-407D-415F-82C3-610B3E7BAC45',
            }
        }]

    def __init__(self):
        BaseParser.__init__(self)

    def parse_list(self, response):
        news_urls = response.xpath('//div[@class="rubricFeed_container__2_OKu"]/a/@href').extract() or ""
        if news_urls:
            for news_url in list(set(news_urls)):
                if not "http" in news_url:
                    news_url = 'https://tass.ru' + news_url
                yield news_url

    def get_title(self, response):
        title = response.xpath('//meta[@property="og:title"]/@content').extract_first(default="") or ""
        news_issue_title = title.strip()
        return news_issue_title or ""

    def get_pub_time(self, response):
        # 2021-08-16T19:40:05+03:00
        info = re.findall('"datePublished":"(\d+-\d+-\d+T\d+:\d+:\d+)', response.text)
        if len(info) > 0:
            time_info = datetime.datetime.strptime(info[0], "%Y-%m-%dT%H:%M:%S") + relativedelta(hours=+5)
            pub_time = self.get_timestamp_by_datetime(time_info)
        else:
            pub_time = self.get_now_timestamp()
        return pub_time

    def get_author(self, response):
        return ""

    def get_content_media(self, response):
        content = []
        media_list_ = []
        news_tags = response.xpath('//div[@class="text-content"]/div/p|'
                                   '//div[@class="image"]/img[@class="image__img"]|'
                                   '//div[@class="text-block"]/p|'
                                   '//div[@class="text-block"]/ul/li/p|'
                                   '//div[@class="text-block"]/ul/li')
        if news_tags:
            for news_tag in news_tags:
                dic = {}
                img_src = news_tag.xpath("./@src").extract_first()
                if not img_src:
                    con = news_tag.xpath('./text()').extract() or ""
                    con = [c.strip() for c in con]
                    con = ''.join([c for c in con if c != ""])
                    dic['content'] = con
                    dic['type'] = 'text'
                else:
                    img_url = news_tag.attrib.get('src')
                    if img_url.startswith("//"):
                        img_url = "https:" + img_url
                    img_dec = news_tag.attrib.get('alt')
                    img_name = self.get_md5_value(img_url) + '.jpg'
                    img_path = img_name
                    dic['content'] = img_path
                    dic['type'] = 'img'
                    media = dict()
                    media['media_type'] = 'img'
                    media['media_url'] = img_url
                    media['path'] = OssPath + img_path
                    media['alt'] = img_dec
                    media_list_.append(media)
                if dic:
                    content.append(dic)
        return content, media_list_
