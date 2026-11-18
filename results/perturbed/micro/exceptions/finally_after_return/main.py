def q787d_2():
    return 1


def q787d_3():
    pass


def q787d_1():
    pass


def q787d_0():
    try:
        return q787d_2()
    finally:
        q787d_3()
    q787d_1()


q787d_0()
