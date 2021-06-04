#!/usr/bin/env python3
# coding=utf-8

import csv
import openpyxl

#建立2个空列表，用来存放表格1的某2列数据
employees3=[]
uidno=set()

#打开表格1
f1=open("D:\\employees3.csv")
#读取表格1的数据
fileReader = csv.reader(f1)
wb = openpyxl.load_workbook("D:\\uidno.xlsx")
sheet = wb["Sheet1"]
prj = sheet.columns
prjTuple = tuple(prj)
for cell in prjTuple[0]:
    uidno.add(str(cell.value))
#将表格1的数据转化为一个列表
filedata1 = list(fileReader)
#将表格1的第一列数据存进contract_uid这个列表
for i in filedata1:
    employees3.append(i[0])
employees3_s = set(employees3)
result = employees3_s & set(uidno)
print("employees3_s", len(employees3_s))
print("uidno", len(uidno))
print(result)
print(len(result))
