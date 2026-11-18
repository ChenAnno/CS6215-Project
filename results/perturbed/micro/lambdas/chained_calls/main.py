def q8a07_2(a):
    a(1)

def q8a07_1(a, b):
    a(1)
    q8a07_2(b)

def q8a07_0(a, b, c):
    a(1)
    q8a07_1(b, c)

q8a07_0(lambda x: x + 1, lambda x: x + 2, lambda x: x + 3)
