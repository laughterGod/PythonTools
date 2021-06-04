#!/usr/bin/env python3
# coding=utf-8

import csv
#建立2个空列表，用来存放表格1的某2列数据
contract_all=[]

#打开表格1
f1=open("D:\\1622096895.csv")
#读取表格1的数据
fileReader = csv.reader(f1)
#将表格1的数据转化为一个列表
filedata1 = list(fileReader)
#将表格1的第一列数据存进contract_uid这个列表
for i in filedata1:
    contract_all.append(i[0:5])

length = len(contract_all)

for i in range(length-1):
    for j in range(i+1, length):
        if contract_all[i][0:3] == contract_all[j][0:3]:
            print(contract_all[i])


