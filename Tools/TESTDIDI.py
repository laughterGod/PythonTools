#!/usr/bin/env python3
# --*-- coding:utf-8 --*--

import sys


def ditu(arr):
    length = len(arr)
    if length == 0:
        return
    params = []
    point_list = arr.split(';')
    length_point = len(point_list)
    for i in range(length_point):
        temp = point_list[i].split(',')
        params.append(temp)
    return params



if __name__ == '__main__':
    arr1 = "-99.15028,19.4342;-99.1503639,19.4339807;-99.150547,19.4335802;-99.150608,19.43338;"
    print(ditu(arr1))