class q64a6_0:
    def __add__(self, other):
        return self

    def __radd__(self, other):
        return self


class q64a6_1(q64a6_0):
    def __radd__(self, other):
        return self


result = q64a6_0() + q64a6_1()
