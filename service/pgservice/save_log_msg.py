from psycopg2.pool import SimpleConnectionPool
from scrapy.utils.project import get_project_settings

from util import tools

settings = get_project_settings()


class PgDeal:
    def __init__(self):
        self.setting = settings["PG_SETTING"]
        self.limit_count = 15  # 最低预启动数据库连接数量
        self.minConn = 5  # 最低预启动数据库连接数量
        self.maxConn = 10
        self.pool = SimpleConnectionPool(self.minConn, self.maxConn,
                                         user=self.setting['User'],
                                         password=self.setting['PassWord'],
                                         host=self.setting['Host'],
                                         port=self.setting['Port'],
                                         database=self.setting['Db'])

    def insertLogs(self, logs):
        conn = self.pool.getconn()
        cursor = conn.cursor()
        data = (logs["code"], logs["msg"], tools.get_time())
        insert_log_sql = f"insert into news_webnsite_log(code,msg,insert_time)value{data}"
        cursor.execute(insert_log_sql)
        self.pool.putconn(conn)

    def close(self, conn, cursor):
        cursor.close()
        conn.close()


mysqlDeal = PgDeal()


