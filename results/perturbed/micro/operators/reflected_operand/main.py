class q5927_1:
    def __add__(self, other):
        return NotImplemented


class q5927_0:
    def __radd__(self, other):
        return self


total = q5927_1() + q5927_0()
count = 1 + q5927_0()
