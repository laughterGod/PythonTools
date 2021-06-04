#!/usr/bin/env python3
# coding=utf-8

import random
import time
import tkinter
import threading


class Main():

    # 初始化
    def __init__(self):
        self.window = tkinter.Tk()
        self.window.title('')
        self.window.geometry('150x150')
        self.btntake = tkinter.Button(self.window, text="开始", width=15, height=2, command=self.take)
        self.btntake.pack()
        self.window.mainloop()

    def take(self):
        #开启线程进行点名操作
        threading.Thread(target=self.run).start()

    def run(self):
        #名字以为每行一个的形式
        f = open('a.txt', 'r', encoding='gbk')
        content = f.read()
        content = content.split()
        begin = int(time.time())
        while True:
            self.btntake['text'] = random.choice(content)
            end = int(time.time())
            if end - begin > 1:
                break


if __name__ == '__main__':
    Main()

