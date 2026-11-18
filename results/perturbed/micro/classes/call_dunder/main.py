class qe0a5_0:
    def __call__(self, x):
        return x + 1


class qe0a5_1:
    def __call__(self, x):
        return x * 2


def qe0a5_2(op, value):
    return op(value)


adder = qe0a5_0()
doubler = qe0a5_1()
qe0a5_2(adder, 1)
