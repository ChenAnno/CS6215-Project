def qd96f_2():
    pass


def qd96f_1():
    pass


def qd96f_0():
    pass


def qd96f_3():
    raise ExceptionGroup("batch", [ValueError("a"), TypeError("b")])


try:
    qd96f_3()
except* ValueError:
    qd96f_2()
except* TypeError:
    qd96f_1()
except* KeyError:
    qd96f_0()
