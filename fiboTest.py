def fibotest(n):
    i, j, k = 0, 1, 1
    arr = []
    while i < n:
        arr.append(j)
        j, k = k, j+k
        i = i+1
    return arr


if __name__ == '__main__':
    print(fibotest(3))

