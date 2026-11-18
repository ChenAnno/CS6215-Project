def q1f25_2():
    pass


class q1f25_0:
    __slots__ = ("callback",)

    def __init__(self, callback):
        self.callback = callback

    def q1f25_1(self):
        self.callback()


q1f25_0(q1f25_2).q1f25_1()
