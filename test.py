#!/usr/bin/env python3
# -*- coding:utf-8 -*-


import sys


def bubble_sort(arr):
    length = len(arr)
    for i in range(length-1):
        for j in range(length-1-i):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]

    return arr


def select_sort(arr):
    length = len(arr)
    for i in range(length-1):
        temp = i
        for j in range(i+1, length):
            if arr[j] < arr[temp]:
                temp = j
        arr[i], arr[temp] = arr[temp], arr[i]
    return arr


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


if __name__ == '__main__':
    Alist = [1,3,2,4,2]
    print(bubble_sort(Alist))
    print(select_sort(Alist))
    print(insert_sort(Alist))
    print(quick_sort(Alist, 0, 4))
    sys.exit(0)




