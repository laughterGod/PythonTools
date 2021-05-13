#!/usr/bin/env python3
# coding=utf-8

import base64
import hmac
import hashlib

def get_basic_auth_str(username, password):
    temp_str = username + ':' + password
    # 转成bytes string
    bytesString = temp_str.encode(encoding="utf-8")
    # base64 编码
    encodestr = base64.b64encode(bytesString)
    # 解码
    decodestr = base64.b64decode(encodestr)
    return 'Basic ' + encodestr.decode()

if __name__ == '__main__':
    print(get_basic_auth_str('price-api', '9239a42935429a1fa007b1661ca994b3'))
