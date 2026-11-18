def q286b_1(func):
    def q286b_2():
        return func()

    return q286b_2


def q286b_0():
    pass


q286b_0 = q286b_1(q286b_0)
q286b_0()
