#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import hmac
import hashlib
import time
from locust import HttpLocust, TaskSet, task, between


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
class UserBehavior(TaskSet):

    @task
    def interface_message(self):
        kop_tools = KopTools()
        time_stamp = kop_tools.get_10_current_timestamp()
        body = ""
        authorization_header = str(time_stamp) + ',' + str(kop_tools.md5_kop(body))
        header = {"Content-Type": "application/json;charset=utf-8", "Authorization": authorization_header}
        response = self.client.post("", data=body.encode('utf-8'), headers=header, verify=False)
        if response.status_code != 200:
            print("fails")
        else:
            print("success")


class WebsiteUser(HttpLocust):
    # weight = 3
    task_set = UserBehavior
    host = ""
    wait_time = between(0.00001, 3)


if __name__ == '__main__':
    import os
    os.system("locust -f kop.py")

