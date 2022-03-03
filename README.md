# HuaWeiCloudMachineGPS![华为云空间](https://id1.cloud.huawei.com/CAS/static_rss/rss_84/CAS/vuebuild/img/cloundLoginLogo.png)

#### 主要功能

-   云监控华为设备状态信息，并存储至数据库
-   检测设备状态变更(在线状态、上线地址状态、网络状态、电量状态)
-   发现设备状态异常变更，则通过PushPlus微信通知
-   发现设备离线，则自动设置设备上线短信通知

---
#### TODO:
- ~~优化地理位置移动分析~~【已完成】
- 简化数据库操作流程
- 避免因设备睡死导致的状态误检测【实验中】
- ~~更换通知渠道~~ 【Pushplus+复活,暂时搁置】
- 启动在线chromedriver，既无需手动配置chromedriver
- 优化设备长期离线处理

---
#### 你需要准备的

- 华为账号、密码
- 数据库地址、账户、密码、数据库名
- [PushPlus](https://pushplus.plus)的Token
- [高德地图坐标拾取器](https://lbs.amap.com/tools/picker) 所需接口参数【新增】
- [Selenium运行环境](https://www.cnblogs.com/rerise/p/14972778.html)

---
#### 数据库组成结构

- 数据库、表名称皆随心、长度要求不严格、充足即可
- 表：login_log

| 字段名  |
|:----:|
|  ID  |
| 设备名  |
|  状态  |
|  地址  |
|  电池  |
| 网络信息 |
| 更新时间 |
| 保存时间 |
- 表：security_log

|  字段名  |
|:-----:|
|  时间   |
|  设备   |
|  标签   |
| 在线状态  |
| 在线情况  |
| 地址状态  |
|  地址   |
| 网络状态  |
|  网络   |
| 电量状态  |
|  电量   |

表：location_log

| 字段名  |
|:----:|
|  id  |
|  省   |
|  市   |
|  区县  |
|  街道  |
| 经纬度  |
|  类型  |
| 完整地址 |
| 查询地址 |
---
#### 注意

> main.py下的save_bug_img为Linux平台路径，自行按照实际情况修改

---
#### 声明

> 本脚本仅用于学习参考、使用者行为与作者无关[GPL3.0]