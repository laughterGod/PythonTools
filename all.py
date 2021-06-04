#!/usr/bin/env python3
# coding=utf-8

import pytest

if __name__ == '__main__':
    # pytest.main() # 执行所有测试case
    # pytest.main(['-vs', './interface_testcase/test_login.py::TestLogin::test_02'])
    # pytest.main(['-vs', './interface_testcase'])
    # pytest.main(['-vs', './interface_testcase/test_login.py', '-n=2']) # 多线程
    pytest.main(['-vs', './interface_testcase/test_login.py', '--reruns=2'])

