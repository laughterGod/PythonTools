#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import sys


# 冒泡
def bubble_sort(arr):
    length = len(arr)
    for i in range(length-1):
        for j in range(length-1-i):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

    return arr


# 选择
def select_sort(arr):
    length = len(arr)
    for i in range(length-1):
        temp = i
        for j in range(i+1, length):
            if arr[j] < arr[temp]:
                temp = j
        arr[i], arr[temp] = arr[temp], arr[i]
    return arr


# 插入
def insert_sort(arr):
    length = len(arr)
    for i in range(length):
        preIndex = i-1
        current = arr[i]
        while preIndex >= 0 and arr[preIndex] >= current:
            arr[preIndex+1] = arr[preIndex]
            preIndex -= 1
        arr[preIndex+1] = current
    return arr


# 快速
def quick_sort(arr, low, high):
    length = len(arr)
    if low >= high:
        return
    i = low
    j = high
    k = arr[low]
    while low < high:
        while low < high and arr[high] >= k:
            high -= 1
        arr[low] = arr[high]
        while low < high and arr[low] <= k:
            low += 1
        arr[high] = arr[low]
    arr[low] = k
    quick_sort(arr, i, low-1)
    quick_sort(arr, low+1, j)
    return arr


# 斐波那契数列
def Fibonacci():
    # 获取用户输入数据
    nterms = int(input("你需要几项？"))

    # 第一和第二项
    n1 = 0
    n2 = 1
    count = 2

    # 判断输入的值是否合法
    if nterms <= 0:
        print("请输入一个正整数。")
    elif nterms == 1:
        print("斐波那契数列：")
        print(n1)
    else:
        print("斐波那契数列：")
        print(n1,",",n2, end=' , ')
        while count < nterms:
            nth = n1 + n2
            print(nth, end=' , ')
            # 更新值
            n1 = n2
            n2 = nth
            count += 1


# 斐波那契数列2
def fibo(num):
    n1 = 0
    n2 = 1
    Alist = [0, 1]
    count = 2

    # 判断输入的值是否合法
    if num <= 0:
       return "请输入一个正整数。"
    elif num == 1:
        return Alist[0:1]
    elif num == 2:
        return Alist
    else:
        while count < num:
            nth = n1 + n2
            Alist.append(nth)
            n1 = n2
            n2 = nth
            count += 1
    return Alist


def fibonacci(n):  # 生成器函数 - 斐波那契
    a, b, counter = 0, 1, 0
    while counter < n:
        yield a
        a, b = b, a + b
        counter += 1


if __name__ == '__main__':
    # Alist = [1,3,2,4,2]
    # print(bubble_sort(Alist))
    # print(select_sort(Alist))
    # print(insert_sort(Alist))
    # print(quick_sort(Alist, 0, 4))
    # Fibonacci()
    # 获取用户输入数据
    # nterms = int(input("你需要几项？"))
    # print(fibo(nterms))
    # print(list(range(10,-1,-1)))
    # f = fibonacci(3)  # f 是一个迭代器，由生成器返回生成
    #
    # while True:
    #     try:
    #         print(next(f), end=" ")
    #     except StopIteration:
    #         sys.exit()
    # sys.exit(0)
    Alist = []
    print(Alist[-1])



