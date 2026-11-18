class q1b23_0(type):
    def q1b23_2(cls):
        return cls()

    def q1b23_3(cls):
        pass


class q1b23_1(metaclass=q1b23_0):
    def __init__(self):
        pass

    def q1b23_3(self):
        pass


q1b23_1.q1b23_2()
q1b23_1().q1b23_3()
