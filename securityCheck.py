# -*- coding: UTF-8 -*-

"""
    # @Project -> File: HuaWeiCloudMachineGPS -> SecurityCheck
    # @IDE: PyCharm
    # @Author : ZZM_T
    # @Date   : 2021/12/19 19:57
    # @Desc   : 【3小时】用于安全状态检测(如：离线后在线通知，登陆地点改变通知)
"""
import time
from mysql import Mysql
from notice import PushPlus


class SecurityCheck:
    def __init__(self):
        self.MySqlDB = Mysql()
        self.Notice = PushPlus()
        self.log = " "
        self.length = 0
        self.status_change = {}
        self.last = 0
        self.least = 0

    def init_log(self):
        """初始化log日志数据"""
        self.log = self.MySqlDB.read_machine_log()
        self.length = len(self.log)
        self.status_change = {
            "UpdateDate": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            "Machine": self.log[self.length - 1][1],
            "ChangeType": "",
            "OnlineStatus": "",
            "Online": "【上次记录】" + self.log[self.length - 1][2],
            "AddressStatus": "",
            "Address": "【上次记录】" + self.log[self.length - 1][3],
            "BatteryStatus": "",
            "Battery": "【上次记录】" + self.log[self.length - 1][4],
            "NetWorkStatus": "",
            "NetWork": "【上次记录】" + self.log[self.length - 1][5],
        }
        # 最新一条log,上一条log
        self.last = self.log[self.length - 1]
        if self.length > 1:
            self.least = self.log[self.length - 2]
        else:
            self.least = self.last

    def online_check(self):
        """在线状态检查"""
        if self.last[2] != self.least[2]:
            self.status_change["OnlineStatus"] = "状态变更"
            self.status_change["Online"] = self.last[2]

    def address_check(self):
        """登录地址变更检查"""
        if self.last[3] != self.least[3]:
            # 发消息警报
            if self.last[3][:2] != self.least[3][:2]:
                # 这是出省了啊
                self.status_change["AddressStatus"] = "省市级变更"
            elif self.last[3][:6] != self.least[3][:6]:
                self.status_change["AddressStatus"] = "市区县级变更"
            elif self.last[3][-6:] != self.least[3][-6:]:
                self.status_change["AddressStatus"] = "乡镇级变更"
            else:
                self.status_change["AddressStatus"] = "位置偏移变更"
            self.status_change["Address"] = self.last[3] + '\n' + self.status_change["Address"]

    def network_check(self):
        """网络信息变更检查"""
        if self.last[5] != self.least[5]:
            # 发消息警报
            mid = int(len(self.last[5]) / 2)
            if self.last[5][:mid] == self.least[5][:mid]:
                self.status_change["NetWorkStatus"] = "变化不大"
            else:
                self.status_change["NetWorkStatus"] = "变化明显"
            self.status_change["NetWork"] = self.last[5]

    def battery_check(self):
        """电池信息变更检查"""
        battery_change = int(self.least[4][:-1]) - int(self.last[4][:-1])
        if battery_change >= 10:
            self.status_change["BatteryStatus"] = "动了动 "
        elif battery_change >= 20:
            self.status_change["BatteryStatus"] = "玩的还可以 "
        elif battery_change >= 30:
            self.status_change["BatteryStatus"] = "玩的太嗨了 "
        elif battery_change < -1:
            self.status_change["BatteryStatus"] = "充电了 "
        self.status_change["Battery"] = self.last[4]
        if self.status_change["BatteryStatus"] != "":
            self.status_change["BatteryStatus"] = self.status_change["BatteryStatus"] + str(battery_change) + "%"

    def set_security_level(self):
        """安全等级定级"""
        if "变化" in self.status_change["NetWorkStatus"]:
            self.status_change["ChangeType"] = " ".join([self.status_change["ChangeType"], "网络变更"])
        if self.status_change["BatteryStatus"] != "":
            self.status_change["ChangeType"] = " ".join([self.status_change["ChangeType"], "玩过"])
        if "变更" in self.status_change["OnlineStatus"]:
            self.status_change["ChangeType"] = " ".join([self.status_change["ChangeType"], "状态变化"])
        if "变更" in self.status_change["AddressStatus"]:
            self.status_change["ChangeType"] = " ".join([self.status_change["ChangeType"], "地理位置变更"])

    def main(self):
        # 更新log
        self.init_log()
        self.online_check()
        self.address_check()
        self.battery_check()
        self.network_check()
        self.set_security_level()
        self.MySqlDB.save_security_log(self.status_change)
        if "地理位置" in self.status_change["ChangeType"] or "玩过" in self.status_change["ChangeType"]:
            self.Notice.send(title="您的设备状态已经发生改变！\n【" + self.status_change["ChangeType"] + " 】",
                             content=self.status_change)


if __name__ == '__main__':
    security = SecurityCheck()
    security.main()
