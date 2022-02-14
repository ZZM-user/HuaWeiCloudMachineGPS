# -*- coding: UTF-8 -*-

"""
    # @Project -> File: HuaWeiCloudMachineGPS -> notice
    # @IDE: PyCharm
    # @Author : ZZM_T
    # @Date   : 2021/12/20 16:31
    # @Desc   : 用于通知[https://pushplus.hxtrip.com/]
"""
import json
import time

import requests


class PushPlus:
    def __init__(self):
        self.push_url = "http://pushplus.hxtrip.com/send"
        self.data = {
            "token": "",
            "title": " ",
            "content": " ",
            "template": "json"
        }

    def send(self, title, content):
        self.data["title"] = title
        self.data["content"] = content
        body = json.dumps(self.data).encode(encoding='utf-8')
        print(body)
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url=self.push_url, data=body, headers=headers, timeout=5)
        if "请求成功" in resp.text:
            print(" Message sent successfully")
        elif "系统繁忙" in resp.text:
            time.sleep(10)
            self.send(title, content)
        print(resp.text)


if __name__ == '__main__':
    title = "Test"
    content = {
        "token": "token",
        "title": "test",
        "content": "这是一个测试",
        "template": "json"
    }
    Notice = PushPlus()
    Notice.send(title, content)
