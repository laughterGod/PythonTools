#!/usr/bin/env python3
# coding=utf-8


class Solution:
    def lengthOfLongestSubstring(self, s: str) -> int:
        length = len(s)
        sub_len = 0
        temp = []
        Alist = list(s)
        for j in range(length):
            for i in range(j, length):
                if Alist[i] not in temp:
                    temp.append(Alist[i])
                    sub_len = max(sub_len, len(temp))
                else:
                    temp.clear()
                    break
        return sub_len

    def removeDuplicates(self, nums):
        col = set(nums)
        numb = len(col)
        string_all = str(numb) + ', nums = ' + str(list(col))

        return string_all

    def removeDuplicates_1(self, nums):
        col = set(nums)
        numb = len(col)
        return numb

if __name__ == "__main__":
    so = Solution()
    # print(so.lengthOfLongestSubstring("pwwkew"))
    print(so.removeDuplicates_1([1,1,2]))
