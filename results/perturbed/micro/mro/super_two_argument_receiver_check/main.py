class q049b_0:
    def q049b_5(self):
        pass


class q049b_2(q049b_0):
    def q049b_5(self):
        pass


class q049b_1(q049b_2):
    pass


class q049b_3:
    def q049b_5(self):
        pass


def q049b_4(obj):
    try:
        super(q049b_2, obj).q049b_5()
    except TypeError:
        pass


q049b_4(q049b_1())
q049b_4(q049b_3())
