# -*- coding: UTF-8 -*-

"""
    # @Project -> File: HuaWeiCloudMachineGPS -> location
    # @IDE: PyCharm
    # @Author : ZZM_T
    # @Date   : 2022/2/21 16:57
    # @Desc   : 通过高德地图API获取指定位置信息
"""
import datetime

import mysql


class Location:
    """
        通过高德地图API获取地理位置信息
    """

    def __init__(self):
        self.gaode_location = "https://restapi.amap.com/v3/place/text"
        self.key = ""
        self.csid = ""
        self.address = ""
        self.headers = {
            "Host": "estapi.amap.com",
            "Connection": "eep-alive",
            "sec-ch-ua": 'Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"",',
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "ozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            "sec-ch-ua-platform": "Windows",
            "Accept": "*/*",
            "Referer": "ttps://lbs.amap.com/",
            "Accept-Encoding": "zip, deflate, br",
            "Accept-Language": "h-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-HK;q=0.6"","
        }
        self.return_location = []
        self.MySqkDB = mysql.Mysql()
        self.log_id = ""

    def get_gaode_api(self):
        """访问高德地图API，获取地理数据"""
        import requests
        params = {
            "s": "rsv3",
            "key": self.key,
            "offset": "1",
            "page": "1",
            "extensions": "all",
            "platform": "JS",
            "appname": "https://lbs.amap.com/tools/picker",
            "csid": self.csid,
            "keywords": self.address
        }
        resp = requests.get(self.gaode_location, headers=self.headers, params=params, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        print(resp.text)
        return None

    def parse_location_json(self, location_json):
        """解析地理位置信息"""
        import jsonpath
        info = {
            "id": self.log_id,
            "province": jsonpath.jsonpath(location_json, "$..pname")[0],
            "city": jsonpath.jsonpath(location_json, "$..cityname")[0],
            "country": jsonpath.jsonpath(location_json, "$..adname")[0],
            "street": jsonpath.jsonpath(location_json, "$..name")[0],
            "location": jsonpath.jsonpath(location_json, "$..location")[0],
            "location_type": jsonpath.jsonpath(location_json, "$..type")[0],
            "full_location": self.address,
        }
        # 对比API获取到的地址，不同则精度不高
        if info["province"] == info["city"]:
            info["lookup_address"] = info["city"] + info["country"] + info["street"]
        else:
            info["lookup_address"] = info["province"] + info["city"] + info["country"] + info["street"]
        self.return_location.append(info)

    def compare_address(self):
        """两个地址做比较及(latitude and longitude)"""
        from math import fabs
        lata_one = self.return_location[0]["location"].split(",")
        lata_two = self.return_location[1]["location"].split(",")
        latitude_differ = fabs(float(lata_two[0]) - float(lata_one[0]))
        longitude_differ = fabs(float(lata_two[1]) - float(lata_one[1]))
        print((latitude_differ, longitude_differ))
        if self.return_location[0]["province"] != self.return_location[1]["province"]:
            return "省级变更"
        if self.return_location[0]["city"] != self.return_location[1]["city"]:
            return "市级变更"
        if self.return_location[0]["country"] != self.return_location[1]["country"]:
            return "区县级变更"
        if self.return_location[0]["street"] != self.return_location[1]["street"]:
            return "街道级变更"
        if not (latitude_differ and longitude_differ):
            return "无变化"
        if latitude_differ < 0.0005 and longitude_differ < 0.0005:
            return "经纬度漂移"

    def main(self, address_one: str, address_two: str, log_id:str):
        """主函数"""
        self.log_id = log_id
        for address in [address_one, address_two]:
            self.address = address
            location_json = self.get_gaode_api()
            self.parse_location_json(location_json)

        print(self.return_location)
        location_change_info = self.compare_address()
        print(location_change_info)
        self.MySqkDB.save_location_log(self.return_location[1])
        # 返回位置变更信息
        return location_change_info, self.return_location


if __name__ == '__main__':
    location_test = Location()
    address_one = " "
    address_two = " "
    location_test.main(address_one, address_two)
    # print(location_test.return_location_json)
