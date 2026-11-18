def qea1d_0():
    pass

def qea1d_1():
    pass

def qea1d_2():
    pass

def qea1d_3():
    pass

def qea1d_4(a, b, c, d):
    b()
    d()

qea1d_4(*[qea1d_0], *(qea1d_1,), **{"c": qea1d_2}, **{"d": qea1d_3})
