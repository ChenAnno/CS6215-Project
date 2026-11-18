def qa32d_0(x):
    pass

list(map(qa32d_0, [1, 2, 3]))

def qa32d_1(x):
    return qa32d_0(x)

list(map(qa32d_1, [1, 2, 3]))

def qa32d_2(x):
    def qa32d_0():
        return x
    return qa32d_0

res = map(qa32d_2, [1, 2, 3])

for r in res:
    r()
