import datetime
import hashlib
import uuid
from urllib import parse

from apps.board_id import board_id
from site_crawl.items import NewsItem
from util.time_deal.translatetTime import twYearDict


def check_img(img_url: str):
    if not img_url:
        return False

    if "data:image" in img_url or "base64" in img_url:
        return False

    return True


def getMD5(*args) -> str:
    return hashlib.md5(str(args).encode()).hexdigest()


def deal_tw_time(time_str: str) -> str:
    """
    @param time_str:111-12-02
    return 2022-12-02
    """
    time_second_part = ""
    if " " in time_str:
        time_second_part = time_str.split(" ")[1]
    time_first_part = time_str.strip().split(" ")[0].split("-")
    time_year = twYearDict.get(time_first_part[0])
    return f"{time_year}-{time_str[1]}-{time_str[2]} {time_second_part}".strip()


def get_time():
    return datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')


def getDomain(url):
    return parse.urlparse(url).netloc


def genUUID(board_name: str) -> str:
    boardNewId = board_id.get(board_name) if board_id.get(board_name) else str(uuid.uuid4())
    print(f"'{board_name}':'{boardNewId},'")
    return boardNewId


def getImage(item: NewsItem):
    imageOrMediaList = []
    for con in item["contents"]:
        initDic = {
            "uuid": "",
            "download_url": "",
            "url_type": "",
            "retry_num": 0,
            "failed_msg": "",
            "site_name": "",
            "site_domain": "",
            "crawl_time": "",
            "last_download_time": "",
            "download_time": "",
            "filename": "",
            "country": "",
        }
        if con["type"] != "text":
            initDic["download_url"] = con["src"]
            initDic["url_type"] = con["type"]
            initDic["uuid"] = item["uuid"]
            initDic["site_name"] = item["channel"].get("source_name")
            initDic["crawl_time"] = get_time()
            initDic["filename"] = con["md5src"]
            initDic["country"] = item["detected_lang"]
            imageOrMediaList.append(initDic)

    return imageOrMediaList


if __name__ == '__main__':
    pass
    # genUUID()
