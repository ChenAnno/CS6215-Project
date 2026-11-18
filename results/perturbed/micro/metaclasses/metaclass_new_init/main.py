class qcea1_0(type):
    def __new__(mcs, name, bases, namespace):
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)


class qcea1_1(metaclass=qcea1_0):
    pass


class qcea1_2(qcea1_1):
    pass
