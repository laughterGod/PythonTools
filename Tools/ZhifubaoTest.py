#!/usr/bin/env python3
# coding=utf-8

import os, fnmatch, math


def test_files(filepath, patterns='*', single_level=False, yield_folder=False):
    if filepath == '':
        print('请填写正确的文件路径')
        return
    patterns = patterns.split(';')
    for path, sub_filepath, files in os.walk(filepath):
        if yield_folder:
            files.extend(sub_filepath)
        files.sort()
        for fname in files:
            for pt in patterns:
                if fnmatch.fnmatch(fname, pt):
                    yield os.path.join(path, fname)
                    break
        if single_level:
            break


def sushu(n):
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


if __name__ == '__main__':
    filesallpath=list(test_files('D:\\\Downloads\\mayijinfu\\', '*_*'))

    for item in filesallpath:
        a = item.split('\\')
        b = a[-1].split('_')
        if sushu(int(b[-1])):
           print(item)
