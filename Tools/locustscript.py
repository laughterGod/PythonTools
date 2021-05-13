#!/usr/bin/env python3
# coding=utf-8

import hmac
import hashlib
import time
import requests
import json
import sys


# 定义工具
class KopTools():

    def sha256_kop(self):
        message = b'Hello, world!'
        key = b'secret'
        h = hmac.new(key, message, digestmod='SHA256')
        # 如果消息很长，可以多次调用h.update(msg)
        return h.hexdigest()

    def md5_kop(self, data):
        return hashlib.md5(data.encode(encoding='UTF-8')).hexdigest()

    # 函数功能：当前时间时间戳的获取10位
    def get_10_current_timestamp(self):
        t = time.time()  # 得到的是一个浮点数，强制类型转换成int类型，就可以获取10位的时间戳
        return int(t)

    # 函数功能：当前时间时间戳的获取13位
    def get_13_current_timestamp(self):
        t = time.time()
        return int(t*1000)


# 定义用户行为
class UserBehavior():

    def interface_message(self):
        kop_tools = KopTools()
        time_stamp = kop_tools.get_10_current_timestamp()
        body = "{\"userId\":\"bytedance-test\",\"sign\":\"38c7b3bc78401b23d782831b80d25979\",\"content\":\"【金山云】您的验证码是321你大飒飒大按是否第三方的防水防汗去年第五套人民币50元、20元、10元、1元纸币纷纷上新，最近新版5元纸币也将亮相去年第五套人民币50元、20元、10元、1元纸币纷纷上新，最近新版5元纸币也将亮相　去年第五套人民币50元、20元、10元、1元纸币纷纷上新，最近新版5元纸币也将亮相，您的验证码是321你大飒飒大按是否第三方的防水防汗去年第五套人民币50元、20元、10元、1元纸币纷纷上新，最近新版5元纸币也将亮相去年第五套人民币50元、20元、10元、1元纸币纷纷上新，最近新版5元纸币也将亮相　去年第五套人民币50元、20元、10元、1元纸币纷纷上新，最近新版5元纸币也将亮相\",\"mobile\":\"18518219486\",\"extCode\":\"5\",\"msgId\":\"test123\",\"ext\":\"test1234\",\"sms_scene\":\"1\",\"callback\":\"http://smscenter.sdns.ksyun.com/api/parse\"}"
        authorization_header = str(time_stamp) + ',' + str(kop_tools.md5_kop(body))
        headers = {"Content-Type": "application/json;charset=utf-8", "Authorization": authorization_header}
        response = requests.post("https://ksmsapi.api.ksyun.com/open/sms/send/bytedance", data=body.encode('utf-8'), headers=headers )
        print(response.text)


if __name__ == '__main__':
    test = UserBehavior()
    test.interface_message()
