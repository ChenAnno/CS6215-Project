def qe206_4():
    pass


def qe206_3():
    pass


class qe206_0:
    handler = staticmethod(qe206_4)


class qe206_2(qe206_0):
    pass


class qe206_1(qe206_0):
    handler = staticmethod(qe206_3)


qe206_2().handler()
