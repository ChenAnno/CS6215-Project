from contextlib import contextmanager


def qd65d_3():
    pass


def qd65d_0():
    raise ValueError("bad")


def qd65d_2():
    pass


@contextmanager
def qd65d_1():
    try:
        yield
    except ValueError:
        qd65d_3()


with qd65d_1():
    qd65d_0()
    qd65d_2()
