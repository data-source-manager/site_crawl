from urllib.parse import unquote

from psycopg2.pool import SimpleConnectionPool
from psycopg2.errors import UniqueViolation
from apps.app import Apps
from service.log.log_deal import log_obj
from site_crawl.pipelines import settings
from util.site_deal.site_board import check_appId_is_dup, siteDeal
from util.time_deal.site_timezone_config import siteTimeZone
from util.tools import getMD5, get_time

site_sql = "insert into site(app_id,site_uuid,site_name,domain,country,language,site_type,time_zone,insert_time,hashvalue) " \
           "values(%d,'%s','%s','%s','%s','%s','%s','%s','%s','%s')"

board_sql = "insert into site_board(site_uuid,board_uuid,board_name,boardurl,req_method,post_url,post_data,header,insert_time,hashvalue) " \
            "values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"


class SaveToMysqlDeal:
    def __init__(self):
        self.setting = settings["PG_SETTING"]
        self.minConn = 5  # 最低预启动数据库连接数量
        self.maxConn = 10
        self.pool = SimpleConnectionPool(self.minConn, self.maxConn,
                                         user=self.setting['User'],
                                         password=self.setting['PassWord'],
                                         host=self.setting['Host'],
                                         port=self.setting['Port'],
                                         database=self.setting['Db'])
        self.channel = siteDeal
        # {site_uuid:{id:x,md5value:xxx}}
        self.siteHashDict = {}
        # {board_uuid:{id:x,md5value:xxx}}
        self.boardHashDict = {}

    def getAllSiteCache(self, cachetype: str):
        conn = self.get_connection()
        cursor = conn.cursor()

        query_sql = ""
        if cachetype == "site":
            query_sql = "select id,site_uuid,hashvalue from site"
        if cachetype == "board":
            query_sql = "select id,board_uuid,hashvalue from site_board"

        cursor.execute(query_sql)
        all_db_res = cursor.fetchall()
        if all_db_res:
            for data in all_db_res:
                data_dict = {"id": data[0], "md5value": data[2]}
                if cachetype == "board":
                    self.boardHashDict[data[1]] = data_dict
                else:
                    self.siteHashDict[data[1]] = data_dict

    def get_connection(self):
        return self.pool.getconn()

    def put_connection(self, connection):
        self.pool.putconn(connection)

    def SaveSite(self):
        self.getAllSiteCache("site")

        conn = self.get_connection()
        cursor = conn.cursor()

        for a in Apps.items():
            site_info = self.channel.site_info(a[0])

            time_zone = siteTimeZone.get(site_info["site_name"])
            if not time_zone:
                time_zone = ""
            else:
                time_zone = time_zone["time_zone"]

            data = (site_info["app_id"], site_info["site_uuid"],
                    site_info["site_name"], site_info["domain"], site_info["country"],
                    "", "", time_zone, get_time())
            md5v = getMD5(data)
            data = data + (md5v,)
            inset_site_sql = site_sql % data
            print(f"写入站点:{data}")

            if self.siteHashDict:
                if self.getAllSiteCache(site_info["site_uuid"]):
                    if md5v != self.getAllSiteCache(site_info["site_uuid"]["md5value"]):
                        # 删除原数据重新写入
                        try:
                            del_sql = f"delete from site where site_id={site_info['site_uuid']}"
                            cursor.execute("BEGIN;")
                            cursor.execute(del_sql)
                            cursor.execute(inset_site_sql)
                            cursor.execute("COMMIT;")
                        except Exception as e:
                            conn.rollback()
                            log_obj.deal_log(f"ave site:{a[0]}error:{e.args}", level="error")
                            continue
                else:
                    cursor.execute(inset_site_sql)
                    conn.commit()
            else:
                cursor.execute(inset_site_sql)
                conn.commit()

        self.put_connection(conn)

    def save_board(self):
        self.getAllSiteCache("board")

        conn = self.get_connection()
        cursor = conn.cursor()
        for x in Apps.items():
            for b in self.channel.site_board_info(x[0]):
                data = (
                    b["site_uuid"], b["board_uuid"], b["board_name"],
                    unquote(b["board_url"]), b["req_method"],
                    unquote(b["post_url"]), b["post_data"], b["header"], get_time()
                )
                md5v = getMD5(data)
                data = data + (md5v,)
                print(f"写入板块{data}")

                insert_board_sql = board_sql % data
                try:
                    if self.boardHashDict:
                        if self.boardHashDict[b["board_uuid"]]:
                            if md5v != self.boardHashDict[b["board_uuid"]]["md5value"]:
                                board_uuid = b['board_uuid']
                                try:
                                    del_sql = f"delete from site where board_uuid='{board_uuid}'"
                                    print(del_sql)
                                    cursor.execute("BEGIN;")
                                    cursor.execute(del_sql)
                                    cursor.execute(insert_board_sql)
                                    cursor.execute("COMMIT;")
                                except Exception as e:
                                    conn.rollback()
                                    log_obj.deal_log(f"save board error:{x[0]}error:{e.args}", level="error")
                                    continue
                        else:
                            cursor.execute(insert_board_sql)
                            conn.commit()
                    else:
                        cursor.execute(insert_board_sql)
                        conn.commit()
                except UniqueViolation as e:
                    conn.rollback()
                    log_obj.deal_log(f"重复板块id:{x}error:{e.args}", level="error")
                    continue

        self.put_connection(conn)


if __name__ == '__main__':
    mysqlSaveDeal = SaveToMysqlDeal()
    if check_appId_is_dup():
        # mysqlSaveDeal.getAllSiteCache("board")
        mysqlSaveDeal.save_board()
