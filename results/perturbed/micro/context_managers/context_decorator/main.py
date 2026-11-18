from contextlib import ContextDecorator


def q7805_1():
    pass


def q7805_2():
    pass


class q7805_0(ContextDecorator):
    def __enter__(self):
        q7805_1()
        return self

    def __exit__(self, *exc):
        q7805_2()
        return False


@q7805_0()
def q7805_3():
    pass


q7805_3()
