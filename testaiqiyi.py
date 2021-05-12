#!/usr/bin/env python3
# --*-- coding:utf-8 --*--


def testArr(arr_A, arr_B):
    if len(arr_A) == 0:
        return arr_B
    elif len(arr_B) == 0:
        return arr_A
    else:
        length_a = len(arr_A)
        length_b = len(arr_B)
        arr_C = []
        k = 0
        for i in range(length_a+1):
            if i == length_a:
                for j in range(k, length_b):
                    arr_C.append(arr_B[j])
                return arr_C
            for j in range(k, length_b):
                if arr_A[i] < arr_B[j]:
                    arr_C.append(arr_A[i])
                    break
                else:
                    arr_C.append(arr_B[j])
                    k += 1
            if i != length_a and k == length_b:
                arr_C.append(arr_A[i])
    return arr_C


if __name__ == '__main__':
    a = [1,2,3,6,7,10]
    b = [4,8,9]
    print(testArr(a, b))

