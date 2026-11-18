class qb2de_0:
    @classmethod
    def qb2de_2(cls):
        return cls()


class qb2de_1(qb2de_0):
    def __init__(self):
        pass

    @classmethod
    def qb2de_2(cls):
        return super().qb2de_2()


qb2de_1.qb2de_2()
