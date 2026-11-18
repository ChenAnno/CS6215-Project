def q5ee2_1(cls):
    original = cls.q5ee2_2

    def q5ee2_2(self):
        return original(self)

    cls.q5ee2_2 = q5ee2_2
    return cls


@q5ee2_1
class q5ee2_0:
    def q5ee2_2(self):
        pass


q5ee2_0().q5ee2_2()
