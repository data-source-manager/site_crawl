from apps.app import Apps
from apps.board_id import board_id
from apps.entry_id import source_dict

from util.exception.exception_t import NoChannelException
from util.tools import getDomain


def get_site_channel_info(channel: dict, appid) -> dict:
    return {
        "meta": {
            'appid': appid,
            'direction': channel.get('direction'),
            'url':channel.get('url'),
            'source_name': channel.get('source_name'),
            'site_board_name': channel.get("site_board_name"),
            'board_theme': channel.get("board_theme"),
            'if_front_position': channel.get("if_front_position"),
            'posturl': channel.get('posturl') or '',
            'headers': channel.get('headers') or '',
            'postdata': channel.get('postdata') or '',
            "board_id": channel.get('board_id') if channel.get('board_id') else board_id.get(
                f"{channel.get('source_name')}_{channel.get('site_board_name')}"),
        },
        "url": channel.get('url')
    }


def getAppId():
    return [a[0] for a in Apps.items()]


def check_appId_is_dup():
    """
    核查appid是否有重复
    """
    flag = True
    appIdList = getAppId()
    appIdSet = set()
    for a in appIdList:
        if a not in appIdSet:
            appIdSet.add(a)
        else:
            print(f"重复id:{a}")
            flag = False
    return flag


def getHashValue(hashdata) -> str:
    return str(hash(hashdata))


def get_channel_info(site_id) -> list:
    """
    获取某个站点下的所有板块信息
    """
    site_channels = []
    channels: list = Apps.get(site_id).appclass.channel
    if not channels:
        raise NoChannelException

    for channel in channels:
        if channel.get("url"):
            site_channels.append(get_site_channel_info(channel, site_id))

    return site_channels


class Site:
    def __init__(self):
        self.boards = []

    def get_site_parser(self, appId):
        return Apps.get(appId).appclass()

    def get_single_site_board(self, site_id) -> list:
        return get_channel_info(site_id)

    def get_all_site_boards(self):
        for appid in Apps.keys():
            self.boards.extend(get_channel_info(appid))

    def site_info(self, appid) -> dict:
        site_info = get_channel_info(appid)[0].get('meta')
        source_name = site_info.get('source_name')
        app_class = self.get_site_parser(appid)
        return {
            "app_id": appid,
            "site_uuid": getattr(app_class, "site_id", "") if getattr(app_class, "site_id", "") else source_dict.get(
                source_name),
            "site_name": source_name,
            "domain": getDomain(site_info.get("url")),
            "country": site_info.get("direction"),
        }

    def site_board_info(self, appid) -> list:
        channels = get_channel_info(appid)
        app_class = self.get_site_parser(appid)
        all_board_list = []
        for c in channels:
            c = c.get("meta")
            source_name = c.get("source_name")
            board_name = c.get("site_board_name")
            site_board_id = c.get("board_id")
            all_board_list.append({
                "site_uuid": getattr(app_class, "site_id", "") if getattr(app_class, "site_id", "") else
                source_dict.get(source_name),
                "board_uuid": site_board_id if site_board_id else board_id.get(f"{source_name}_{board_name}"),
                "board_name": board_name,
                "board_theme": c.get("board_theme"),
                "board_url": c.get("url"),
                "req_method": "post" if c.get("post_url") else "get",
                "post_url": c.get("post_url", ""),
                "post_data": c.get("post_data", ""),
                "header": c.get("header", ""),
            })
        return all_board_list


siteDeal = Site()


if __name__ == '__main__':
    t = Site().site_info(3044)
    print(t)