def q3cc0_0():
    pass

def q3cc0_1(a):
    return a

def q3cc0_2():
    return q3cc0_1

q3cc0_2()(q3cc0_0)()
