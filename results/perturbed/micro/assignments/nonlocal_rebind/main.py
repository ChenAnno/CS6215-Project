def qb91c_0():
    pass

def qb91c_1():
    pass

def qb91c_3():
    handler = qb91c_0

    def qb91c_2():
        nonlocal handler
        handler = qb91c_1

    qb91c_2()
    handler()

qb91c_3()
