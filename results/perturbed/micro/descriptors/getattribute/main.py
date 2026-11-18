def q5bd0_1(name):
    pass


class q5bd0_0:
    def __getattribute__(self, name):
        q5bd0_1(name)
        return object.__getattribute__(self, name)

    def q5bd0_2(self):
        pass


q5bd0_0().q5bd0_2()
