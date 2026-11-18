def q9356_2(obj):
    return True


class q9356_1(type):
    def __instancecheck__(cls, obj):
        return q9356_2(obj)


class q9356_0(metaclass=q9356_1):
    pass


def q9356_4():
    return isinstance(1, q9356_0)


def q9356_3():
    return isinstance(q9356_0(), q9356_0)


q9356_4()
q9356_3()
