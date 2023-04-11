import enum


class EAppClassify(enum.Enum):
    """App类型境内境外枚举"""

    # 境内
    Domestic = 1
    # 境外
    Abroad = 2


class AppConfig:
    """表示一个采集端插件的类型字典和固定参数配置。
    appname: app名字
    appclass: app插件的实现类
    apptype: app类型境内境外枚举。
    appdomain: app初始域名
    """
    def __init__(
            self,
            appid: int,
            appname: str,
            # apptype: EAppClassify,
            appclass: type,
            appdomain: str
    ):
        if not isinstance(appid, int) or appid == '':
            raise Exception("Param appid is invalid.")
        if not isinstance(appname, str) or appname == '':
            raise Exception("Param appname is invalid.")
        # if not isinstance(apptype, EAppClassify):
        #     raise Exception("Param apptype is invalid.")
        if not isinstance(appclass, type):
            raise Exception("Param appclass is invalid.")
        if not isinstance(appdomain, str):
            raise Exception("Param appurl is invalid.")

        self.appid: int = appid
        self.appname: str = appname
        # self.apptype: EAppClassify = apptype
        self.appclass: type = appclass
        self.appdomain: str = appdomain
