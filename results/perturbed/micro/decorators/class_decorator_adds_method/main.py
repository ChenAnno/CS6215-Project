def q784a_1(self):
    pass


def q784a_2(cls):
    cls.q784a_1 = q784a_1
    return cls


@q784a_2
class q784a_0:
    pass


q784a_0().q784a_1()
