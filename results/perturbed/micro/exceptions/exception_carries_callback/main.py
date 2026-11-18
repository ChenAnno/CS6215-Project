def q73a6_2():
    pass


def q73a6_3():
    pass


class q73a6_0(Exception):
    def __init__(self, action):
        super().__init__()
        self.action = action


def q73a6_1():
    raise q73a6_0(q73a6_2)


def q73a6_4():
    raise q73a6_0(q73a6_3)


try:
    q73a6_1()
except q73a6_0 as error:
    error.action()
