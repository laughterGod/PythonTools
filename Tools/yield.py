#!/usr/bin/env python3
# coding=utf-8


# 斐波那契
def fibonacci():
    a=b=1
    yield a
    yield b
    while True:
        a,b = b,a+b
        yield b


# 通过固定长度的缓冲区不断读文件，防止一次性读取出现内存溢出
def read_file(path):
    SIZE = 10
    with open(path,'r') as f:
        while True:
            block = f.read(SIZE)
            if block:
                yield block
            else:
                return


if __name__ == '__main__':
    c = read_file('D:\\\Downloads\\mayijinfu\\Testyield.txt')
    for item in c:
        print(item)
    # print(c.__next__())

    for num in fibonacci():
        if num > 100:
            break
        print(num)


