# -*- coding: UTF-8 -*-

"""
    # @Project -> File: HuaWeiCloudMachineGPS -> mysql
    # @IDE: PyCharm
    # @Author : ZZM_T
    # @Date   : 2021/12/19 22:47
    # @Desc   : 数据库增删改查操作
"""
import datetime

import pymysql
from pymysql import err
from pymysql.constants import COMMAND


class Mysql:
    def __init__(self):
        self.host = "127.0.0.1"
        self.user = "root"
        self.password = "roo"
        self.database = "huaweimachinegps"
        self.port = 3306
        self.charset = "utf8"
        # 创建连接
        self.con = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,
                                   port=self.port,
                                   charset=self.charset)
        # 创建游标
        self.cur = self.con.cursor()
        self.sign = True

    def ping(self, reconnect=True):
        """判断连接是否断开，重连"""
        if self._sock is None:
            if reconnect:
                self.connect()
                reconnect = False
            else:
                raise err.Error("Database Already closed")
        try:
            self._execute_command(COMMAND.COM_PING, "")
            self._read_ok_packet()
        except Exception:
            if reconnect:
                self.connect()
                self.ping(False)
            else:
                raise

    def execute_sql(self, sql: str):
        """执行SQL语句"""
        try:
            self.con.ping()
            if sql[:6] == "select":
                self.cur.execute(sql)
                result = self.cur.fetchall()
            else:
                self.cur.execute(sql)
        except Exception as ex:
            print(ex)
            print(' execute_sql fail : ', sql)
            self.sign = False
        finally:
            # 提交事务
            self.con.commit()
            # 释放游标
            self.cur.close
            # 关闭连接
            self.con.close()
        if self.sign:
            print(" execute_sql succeed! : ", sql)
            if sql[:6] == "select":
                return result

    def save_login_log(self, info: dict):
        """保存设备定位信息"""
        keys = list(info.keys())
        # 构建时间戳id
        id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

        insert_comm = 'insert into login_log values({0},"{1}","{2}","{3}","{4}","{5}","{6}","{7}");'.format(
            id, info[keys[0]], info[keys[1]], info[keys[2]], info[keys[3]],
            info[keys[4]], info[keys[5]], info[keys[6]])
        self.execute_sql(insert_comm)

    def read_machine_log(self):
        """读取设备定位日志"""
        sql = "select * from login_log;"
        log = self.execute_sql(sql)
        return log

    def save_security_log(self, info: dict):
        """保存安全日志"""
        keys = list(info.keys())
        sql = 'insert into security_log values("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}");'.format(
            info[keys[0]], info[keys[1]], info[keys[2]], info[keys[3]], info[keys[4]],
            info[keys[5]], info[keys[6]], info[keys[7]], info[keys[8]], info[keys[9]], info[keys[10]])
        self.execute_sql(sql)

    def save_location_log(self, info: dict):
        """写入位置信息记录"""
        keys = list(info.keys())
        sql = 'insert into location_log values("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}");'.format(
            info[keys[0]], info[keys[1]], info[keys[2]], info[keys[3]], info[keys[4]],
            info[keys[5]], info[keys[6]], info[keys[7]], info[keys[8]])
        self.execute_sql(sql)


if __name__ == '__main__':
    db = Mysql()
    print(db.read_machine_log(), len(db.read_machine_log()))
