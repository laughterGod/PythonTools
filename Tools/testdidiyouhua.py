#!/usr/bin/env python3
# coding=utf-8

import math


def sushu(n):
    for i in range(2, int(math.sqrt(n))+1):
        if n % i == 0:
            return False
    return True

def testsushu(start, end):
    a = []
    if not (isinstance(start, int) and isinstance(end, int)):
        return "参数错误！"
    if start > end:
        return "参数错误！"
    for i in range(start, end+1):
        if sushu(i):
            a.append(i)
    return a


def testarr(a, b):
    c = []
    pa, pb = 0, 0
    length_a = len(a)
    length_b = len(b)
    while pa < length_a or pb < length_b:
        if pa == length_a:
            c.append(b[pb])
            pb += 1
        elif pb == length_b:
            c.append(a[pa])
            pa += 1
        elif a[pa] < b[pb]:
            c.append(a[pa])
            pa += 1
        else:
            c.append(b[pb])
            pb += 1
    return c


if __name__ == '__main__':
    a = [-100, 1, 10, 100]
    b = [0, 1, 5, 1000]
    # print(testsushu(1000, 10000))
    print(testarr(a, b))
