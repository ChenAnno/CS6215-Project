class qdab1_0:
    def __new__(cls, *args):
        return args[0]


class qdab1_3(qdab1_0):
    pass


class qdab1_1(qdab1_0):
    pass


class qdab1_2:
    def qdab1_8(self):
        pass


class qdab1_4:
    def qdab1_8(self):
        pass


def qdab1_5(*args):
    return args[0]


def qdab1_6():
    pass


def qdab1_7():
    pass


a = qdab1_5(qdab1_6)
b = qdab1_5(qdab1_7)
a()
qdab1_3(qdab1_2()).qdab1_8()
qdab1_1(qdab1_4())
