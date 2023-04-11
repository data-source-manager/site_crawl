from urllib.parse import urlparse

import requests
import scrapy
from lxml import etree

from site_crawl.settings import EN_PROXY, proxy

chrome75_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' +
                                  'Chrome/75.0.3770.142 Safari/537.36'}
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36"
}


# 针对facebook,twitter等接口获取点赞,分享等
def request_interface(xpaths, reponse_url, interface_url=None, proxy=None) -> int:
    '''

    :param xpaths: xpaths=> xpaths.read_count or xpaths.like_count
    :param reponse_url: 请求的url
    :return:
    '''
    # url 域名可以是facebook,twitter等　根据实际网站接口去改
    if proxy is None:
        proxy = {}
    url = 'https://www.facebook.com/plugins/like.php?'

    params_data = {
        'app_id': '',
        # channel 为固定链接，只需复制
        'channel': 'https://staticxx.facebook.com/x/connect/xd_arbiter/?version=46#cb=f23de6232daff6&domain=www.dphk.org&is_canvas=false&origin=https%3A%2F%2Fwww.dphk.org%2Ff1c1031bdb79454&relation=parent.parent',
        'container_width': '0',
        'href': reponse_url,
        'layout': 'button_count',
        'locale': 'zh_HK',
        'sdk': 'joey',
        'send': False,
        'show_faces': False,
        'width': 90
    }
    url = interface_url if interface_url else url
    res = requests.get(url, params=params_data, headers=headers, proxies=proxy)

    html_root = etree.HTML(res.text)

    xpath_count_str = html_root.xpath(xpaths)

    if xpath_count_str:
        xpath_count = int(xpath_count_str.replace(",", ""))

    else:
        xpath_count = None

    return xpath_count


def facebook_like_count_interface(reponse_url, xpath) -> int:
    """
    :param xpaths: xpaths=> xpaths.read_count or xpaths.like_count
    :param reponse_url: 请求的url
    :param
    :return:
    """
    domain = urlparse(reponse_url).netloc
    url = f"https://www.facebook.com/v4.0/plugins/like.php?action=like&app_id=1722151021422152&channel=https%3A%2F%2Fstaticxx.facebook.com%2Fx%2Fconnect%2Fxd_arbiter%2F%3Fversion%3D46%23cb%3Df343359a5800594%26domain%3D{domain}%26is_canvas%3Dfalse%26origin%3Dhttps%253A%252F%252F{domain}%252Ff4cd5789be927%26relation%3Dparent.parent&container_width=0&href={reponse_url}&layout=button_count"
    if EN_PROXY:
        response = requests.get(url.format(), headers=chrome75_headers, proxies=proxy)
    else:
        response = requests.get(url.format(), headers=chrome75_headers)
    html_root = scrapy.Selector(text=response.text)

    like_count = "".join(html_root.xpath(xpath).extract())
    if like_count:
        return int(like_count.replace(",", ""))
    return 0


if __name__ == '__main__':
    request_interface("https://www.upmedia.mg/news_info.php?Type=1&SerialNo=153092",
                      "")
