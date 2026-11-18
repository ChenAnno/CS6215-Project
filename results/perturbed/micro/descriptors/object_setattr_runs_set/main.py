def qb629_2(value):
    pass


class qb629_0:
    def __set__(self, obj, value):
        qb629_2(value)


class qb629_1:
    value = qb629_0()

    def __init__(self, value):
        object.__setattr__(self, "value", value)


qb629_1(1)
