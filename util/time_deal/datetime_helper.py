import time
import traceback
from datetime import datetime, timedelta

import parsedatetime
from dateutil import parser

from service.log.log_deal import log_obj
from util.exception.exception_t import ValueException, NoSiteException
from util.time_deal.site_timezone_config import siteTimeZone, timeNumDict


def fuzzy_parse(fuzzy_string: str) -> int:
    """
    解析一段字符串中包含的日期时间。目前不支持时区自动抽取
    TODO 添加时区解析的支持和详尽测试
    :param fuzzy_string: 包含日期时间的字符串
    :return: 时间戳
    >>> fuzzy_parse("<!-- ITEMDATE: 2021-11-30 00:00:00 GMT -->")
    1638201600
    >>> fuzzy_parse("Nov 30th 2021")  # 经济学人
    1638201600
    >>> fuzzy_parse("November 30, 2021")  # AP
    1638201600
    >>> fuzzy_parse("Updated Nov. 30, 2021, 0:00 a.m. ET")  # NY Times
    1638201600
    """
    return int(fuzzy_parse_datetime(fuzzy_string).timestamp())


def fuzzy_parse_datetime(fuzzy_string: str):
    """
    >>> fuzzy_parse_datetime("Nov 30th 2021") == datetime(2021, 11, 30, 0, 0, 0)  # The Economist
    True
    >>> fuzzy_parse_datetime("November 30, 2021") == datetime(2021, 11, 30, 0, 0, 0)  # AP
    True
    >>> fuzzy_parse_datetime("Updated Nov. 30, 2021, 0:00 a.m. ET") == datetime(2021, 11, 30, 0, 0, 0)  # NY Times
    True
    >>> fuzzy_parse_datetime("Today at 6:15 p.m. EST").time()   # The Washington Post
    datetime.time(18, 15)
    >>> # fuzzy_parse_datetime("2021年12月1日")  # 不支持

    """
    cal = parsedatetime.Calendar()

    # parse_status 可能的结果：
    # 0 = not parsed at all
    # 1 = parsed as a date
    # 2 = parsed as a time
    # 3 = parsed as a datetime
    ts, parse_status = cal.parse(fuzzy_string)

    if parse_status == 0:
        raise RuntimeError(f"解析日期时发生错误：{fuzzy_string}")
    elif parse_status == 1:
        parsed_dt = (list(ts[:3]) + [0, 0, 0])
    else:
        parsed_dt = ts[:6]

    return datetime(*parsed_dt)


def getHoursBySiteZone(site_zone: str)->int:
    if not site_zone:
        log_obj.deal_log(f"site_zone can't  be empty", level='error')
        return 0

    hours = 0
    if site_zone.startswith("东"):
        hours = 8 - timeNumDict.get(site_zone[1])
    if site_zone.startswith("西"):
        hours = 8 + timeNumDict.get(site_zone[1])
    return hours


def parseTimeWithOutTimeZone(formatdate: datetime, site_name=None, hours=None) -> str:
    """
    解析不含时区的时间，
    %a 英文星期简写 %A 英文星期的完全
    %b 英文月份的简写 %B 英文月份的完全
    %c 显示本地日期时间
    %d 日期，取1-31
    %H 小时， 0-23
    %m 月， 01 -12
    %M 分钟，1-59
    %j 年中当天的天数
    %w 显示今天是星期几
    %W 第几周
    %x 当天日期
    %X 本地的当天时间
    %y 年份 00-99间
    %Y 年份的完整拼写
    字符串时间转datetime类型时间: datetime.strptime(timeStr, "%Y/%m/%d")
    @param formatdate: ex: "YYYY-mm-dd HH:MM:SS" 2022-12-09 16:33:00,
    @param hours: ex:同区相减,异区相加, 西一区 转东八区,hours=9 东一区转东八区 hours=7
    @param site_name:站点名
    """

    try:
        if not isinstance(formatdate, datetime):
            raise ValueException

        if not hours and not site_name:
            log_obj.deal_log(f"hours or site_name can't all be empty", level='error')
            return ""

        if site_name:
            siteZone = siteTimeZone.get(site_name.strip())
            if siteZone:
                siteZone = siteZone.get("time_zone")
                hours = getHoursBySiteZone(siteZone)
            else:
                raise NoSiteException

        return str(formatdate + timedelta(hours=hours))
    except ValueException as e:
        log_obj.deal_log(f"不是一个datetime类型的时间", level='error')
        raise ValueException
    except:
        log_obj.deal_log(f"time trans error,err:{traceback.format_exc()}", level='error')
        return "9999-01-01 00:00:00"


def parseTimeWithTimeZone(fuzzy_string: str) -> str:
    """
    解析含时区的时间
    @param fuzzy_string:ex input:2022-12-09T16:33:00.000Z output:2022-12-10 00:33:00
    """
    try:
        timeStamp = fuzzy_parse_timestamp(fuzzy_string)
        return str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timeStamp)))
    except:
        return "9999-01-01 00:00:00"


def fuzzy_parse_timestamp(fuzzy_string: str) -> int:
    """
    >>> fuzzy_parse_timestamp("2022-03-26T07:25:42+09:00")
    0
    """
    return int(parser.parse(fuzzy_string).timestamp())


def it_time_helper(time_str):
    """
    意大利
        20 April 2020 => 时间格式
     """
    month_dict = {
        'gennaio': '1',
        'febbraio': '2',
        'marzo': '3',
        'aprile': '4',
        'maggio': '5',
        'giugno': '6',
        'luglio': '7',
        'agosto': '8',
        'settembre': '9',
        'ottobre': '10',
        'novembre': '11',
        'dicembre': '12'
    }
    try:
        time_str = time_str.lower()
        for month in month_dict:
            time_str = time_str.replace(month, month_dict.get(month))
        date_obj = datetime.strptime(time_str, "%d %m %Y")
        res = date_obj.strftime("%Y-%m-%d  %H:%M:%S")
        return str(res)
    except Exception as e:
        return "9999-01-01 00:00:00"


def tw_timehelper(time_str, fmt):
    """
    台湾时间转换
    111/07/15 => datetime.datetime
    """
    time_dic = {
        '89': 2000,
        '90': 2001,
        '91': 2002,
        '92': 2003,
        '93': 2004,
        '94': 2005,
        '95': 2006,
        '96': 2007,
        '97': 2008,
        '98': 2009,
        '99': 2010,
        '100': 2011,
        '101': 2012,
        '102': 2013,
        '103': 2014,
        '104': 2015,
        '105': 2016,
        '106': 2017,
        '107': 2018,
        '108': 2019,
        '109': 2020,
        '110': 2021,
        '111': 2022,
        '112': 2023,
        '113': 2024,
        '114': 2025,
        '115': 2026,
        '116': 2027,
        '117': 2028,
        '118': 2029,
        '119': 2030,
    }
    try:
        for year in time_dic:
            time_str = time_str.replace(year, time_dic[year])
        return datetime.strptime(time_str, fmt)
    except:
        return None


def __doc_test(verbose: bool = True):
    import doctest
    doctest.testmod(verbose=verbose)


if __name__ == "__main__":
    print(getHoursBySiteZone("东九区"))
