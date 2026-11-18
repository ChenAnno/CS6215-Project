from contextlib import contextmanager


def q528e_0():
    pass


def q528e_2():
    pass


@contextmanager
def q528e_1():
    q528e_0()
    try:
        yield "resource"
    finally:
        q528e_2()


with q528e_1() as resource:
    pass
