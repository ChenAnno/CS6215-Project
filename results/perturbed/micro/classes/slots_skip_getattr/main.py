def q226a_3():
    pass


def q226a_1():
    pass


class q226a_0:
    __slots__ = ("action",)

    def __init__(self, action):
        self.action = action

    def __getattr__(self, name):
        return q226a_1

    def q226a_2(self):
        self.action()


q226a_0(q226a_3).q226a_2()
