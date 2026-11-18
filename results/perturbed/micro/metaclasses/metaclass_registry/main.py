registry = {}


class q1c6b_2(type):
    def __init__(cls, name, bases, namespace):
        super().__init__(name, bases, namespace)
        registry[name] = cls


class q1c6b_0(metaclass=q1c6b_2):
    def q1c6b_3(self):
        pass


class Alpha(q1c6b_0):
    def q1c6b_3(self):
        pass


class q1c6b_1(q1c6b_0):
    def q1c6b_3(self):
        pass


registry["Alpha"]().q1c6b_3()
