# -*- coding: UTF-8 -*-

"""
    # @Project -> File: HuaWeiCloudMachineGPS -> main.py
    # @IDE: PyCharm
    # @Author : ZZM_T
    # @Date   : 2021/12/19 16:45
    # @Desc   :  华为云服务监控设备定位
"""
import time
import os
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from mysql import Mysql
from notice import PushPlus
from securityCheck import SecurityCheck


class HuaWeiCloudMachineGPS:
    def __init__(self):
        self.account = ''
        self.password = ''
        self.url = 'https://cloud.huawei.com/'
        # 无头浏览器
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('lang=zh_CN.UTF-8')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('blink-settings=imagesEnabled=false')
        # self.options.add_argument(
        #     'user-agent="User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"')
        self.driver = webdriver.Chrome(options=self.options)
        # 隐式等待
        self.driver.implicitly_wait(60)
        # 设备名、设备状态、物理地址、电池信息、网络信息、更新时间、保存时间
        self.info = {
            "Machine": "",
            "Status": "",
            "Address": "",
            "Battery": "",
            "NetWork": "",
            "UpdateTime": "",
            "SaveTime": "",
        }
        self.MySqlDB = Mysql()
        self.log_length = len(self.MySqlDB.read_machine_log())
        if self.log_length:
            self.Security = SecurityCheck()
        self.Notice = PushPlus()
        self.save_bug_img = "/opt/task/HuaWeiCloudMachineGPS/bugPrtScreen/"

    def find_by_xpath(self, locator, timeout=None):
        """通过xpath获取元素 包含等待"""
        if not timeout:
            timeout = 60
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, locator))
            )
            print('\n Find by xpath is found : ', locator)
            return element
        except TimeoutException:
            print('\n Find by xpath not found : ', locator)
            print(TimeoutException)
            self.prt_screen()
            return None

    def prt_screen(self):
        """页面截图"""
        if not os.path.exists(self.save_bug_img):
            os.mkdir(self.save_bug_img)
            print("初始化目录 " + self.save_bug_img)
        img_name = time.strftime("%Y-%m-%d-%H_%M_%S", time.localtime(time.time()))
        folder = self.save_bug_img + "/" + img_name[:-9]
        if not os.path.exists(folder):
            os.mkdir(folder)
            print("初始化目录 " + folder)
        self.driver.get_screenshot_as_file(folder + '/' + img_name + '.png')
        print("\n截图成功：" + folder + img_name)

    def change_language(self):
        """切换浏览器语言：当前设置为中文"""
        if "华为" in self.driver.title:
            print("\n The current language is Simplified Chinese")
            return
        js = "div = document.getElementById('wrapper');div.style.overflow='visible';div.style.top='-2700px';"
        self.driver.execute_script(js)
        print("\n JavaScript " + js + " executed")
        # 点击切换语言
        self.find_by_xpath("//span[contains(@class,'langBtn')]").click()
        # 选择要切换的语言 ：简体中文
        # self.find_by_xpath("//li[@code='ko-kr']").click()
        self.find_by_xpath("//li[@code='zh-cn']").click()
        time.sleep(1.5)
        if "华为" in self.driver.title:
            print(" The language is " + self.find_by_xpath("//span[contains(@class,'langBtn')]").text)

    def login(self):
        """登录账号"""
        self.driver.get(self.url)
        # 切换语言
        self.change_language()
        # 切换至表单
        self.driver.switch_to.frame("frameAddress")
        # 寻找并输入账号
        self.find_by_xpath("//input[contains(@class,'hwid-input userAccount')]").send_keys(self.account)
        # 寻找并输入密码
        self.find_by_xpath("//input[@class='hwid-input hwid-input-pwd']").send_keys(self.password)
        time.sleep(1.5)
        # 执行登陆动作
        self.find_by_xpath("//div[@class='normalBtn']").click()
        time.sleep(2.5)
        if self.find_by_xpath("//div[@id='userName']") is not None:
            print("\n Account Login succeeded! : " + self.account)
            return True
        print("\n Account login failure! : " + self.account)
        return False

    def switch_to_find_devices(self):
        """切换至查找设备"""
        self.find_by_xpath("//div[@class='warpHome mobile']").click()
        time.sleep(1.6)
        if self.find_by_xpath("//div[@class='header_name_item']") is None:
            return False
        print("\n The location information screen is displayed!")
        return True

    def online_notice(self):
        """离线通知"""
        if self.find_by_xpath("//div[contains(@class,'notify_info_red')]") is None:
            return
        # 设置通知方式
        self.find_by_xpath("//div[contains(@class,'notify_info_red')]").click()
        # 输入手机号
        self.find_by_xpath("//input[contains(@class,'has-country-list')]").send_keys(self.account)
        # 确定
        self.find_by_xpath("//div[contains(@class,'dialog_button enable')]").click()
        print("A device offline notification has been sent. Procedure")

    def collect_info(self):
        """获取设备信息"""
        time.sleep(10)
        # 设备名、设备状态、物理地址、电池信息、网络信息、更新时间、保存时间
        self.info["Machine"] = self.find_by_xpath("//div[@class='header_name_item']").text
        self.info["Status"] = self.find_by_xpath("//div[contains(@class,'device_status')]").text
        if "离线" in self.info["Status"]:
            print("\n Device status: Offline")
            self.online_notice()
            self.info["UpdateTime"] = self.find_by_xpath("//div[@class='notify_info']").text
            self.find_by_xpath("//div[@class='notify_info']").click()
            self.info["NetWork"] = self.find_by_xpath("//span[@class='offLineContentDetailTxt']").text
            self.info["Address"] = self.find_by_xpath("//span[@class='offLineContentDetail']").text
        else:
            print("\n Device status: Online")
            self.info["NetWork"] = self.find_by_xpath("//span[@class='device_wlan_info']").text
            self.info["Address"] = self.find_by_xpath("//div[contains(@class,'offLineInfo')]").text
            self.info["UpdateTime"] = self.find_by_xpath("//span[@class='updateTime']").text
            if "前更新" in self.info["UpdateTime"]:
                self.driver.refresh()
                self.collect_info()
        self.info["Battery"] = self.find_by_xpath("//div[contains(@class,'batteryPower')]").text
        self.info["SaveTime"] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

    def main(self):
        try:
            if self.login():
                if self.switch_to_find_devices():
                    self.driver.refresh()
                    time.sleep(2.5)
                    self.collect_info()
                    # 检测状态 判断是否发送离线通知
                    if "离线" in self.info["Status"]:
                        self.Notice.send(title="您的设备处于离线状态", content=self.info)
                    self.MySqlDB.save_login_log(self.info)
                    # 检测log长度 首次运行不做安全检测
                    if self.log_length:
                        self.Security.main()
                    # self.Notice.send(title="设备例行记录", content=self.info)
        except Exception as e:
            print(e)
            self.prt_screen()
            self.Notice.send(title="你的程序出现问题了: HuaWeiCloudMachineGPS", content=str(e))
        finally:
            self.driver.quit()


if __name__ == '__main__':
    MachineOne = HuaWeiCloudMachineGPS()
    MachineOne.main()
