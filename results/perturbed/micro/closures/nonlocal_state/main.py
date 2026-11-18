def qd52f_1():
    pass

def qd52f_2():
    pass

def qd52f_3():
    current = qd52f_1

    def qd52f_4():
        nonlocal current
        current = qd52f_2

    def qd52f_0():
        current()

    return qd52f_4, qd52f_0

qd52f_4, qd52f_0 = qd52f_3()
qd52f_4()
qd52f_0()
