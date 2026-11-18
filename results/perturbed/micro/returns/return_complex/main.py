def qbefb_0():
    return 1 + 1

qbefb_0()


def qbefb_1():
    return 1

def qbefb_2():
    return qbefb_1

def qbefb_3(a):
    return qbefb_2()

qbefb_3(1)()

def qbefb_4():
    return qbefb_1() + 1

qbefb_4()
