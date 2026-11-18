def q7b78_2():
    pass


class q7b78_1(type):
    def __getattr__(cls, name):
        return q7b78_2


class q7b78_0(metaclass=q7b78_1):
    pass


q7b78_0.anything()
