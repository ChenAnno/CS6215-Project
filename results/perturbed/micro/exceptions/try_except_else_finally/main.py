def qb422_5():
    raise ValueError("bad")


def qb422_6():
    pass


def qb422_3():
    pass


def qb422_0():
    pass


def qb422_4():
    pass


def qb422_1():
    pass


def qb422_2():
    pass


try:
    qb422_5()
except ValueError:
    qb422_3()
else:
    qb422_0()
finally:
    qb422_2()

try:
    qb422_6()
except ValueError:
    qb422_4()
else:
    qb422_1()
finally:
    qb422_2()
