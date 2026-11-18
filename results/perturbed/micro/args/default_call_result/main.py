def qb2a8_0():
    pass

def qb2a8_1():
    return qb2a8_0

def qb2a8_2(f=qb2a8_1()):
    f()

qb2a8_2()
