#!/usr/bin/env python3
# coding=utf-8


class QueueTest:

    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        return self.items.pop(0)

    def empty(self):
        return self.size() == 0

    def size(self):
        return len(self.items)


def josephus(namelist, num):
    simqueue = QueueTest()
    for name in namelist:
        simqueue.enqueue(name)

    while simqueue.size() > 1:
        for i in range(num):
            simqueue.enqueue(simqueue.dequeue())

        simqueue.dequeue()
        print(simqueue.items)

    return simqueue.dequeue()


if __name__ == '__main__':
    print(josephus(["Bill", "David", "Kent", "Jane", "Susan", "Brad"], 3))
