#!/usr/bin/env python3
# --*-- coding:utf-8 --*--
import math


def sushu(n):
    for i in range(2, int(math.sqrt(n)+1)):
        if n % i == 0:
            return False
    return True


def testsushu(m):
    arr = []
    for i in range(1000, m+1):
        if sushu(i):
            arr.append(i)
    return arr


def testarr1(a, b):
    c = []
    lengt_a = len(a)
    lengt_b = len(b)
    pa, pb = 0, 0
    while pa < lengt_a or pb < lengt_b:
        if pa == lengt_a:
            c.append(b[pb])
            pb += 1
        elif pb == lengt_b:
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
    # print(testarr1(a, b))
    print(testsushu(10000))
