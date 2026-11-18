def qad84_2():
    pass


def qad84_1():
    raise ValueError("bad")


def qad84_3():
    pass


class qad84_0:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        qad84_2()
        return True


with qad84_0():
    qad84_1()
    qad84_3()
