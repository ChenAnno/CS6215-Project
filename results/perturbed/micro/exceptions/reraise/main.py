def q536a_1():
    raise ValueError("bad")


def q536a_0():
    pass


def q536a_2():
    pass


def q536a_3():
    try:
        q536a_1()
    except ValueError:
        q536a_0()
        raise


try:
    q536a_3()
except ValueError:
    q536a_2()
