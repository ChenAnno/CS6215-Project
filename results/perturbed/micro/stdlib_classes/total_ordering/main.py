import functools


@functools.total_ordering
class qfbda_0:
    def __init__(self, number):
        self.number = number

    def __eq__(self, other):
        return self.number == other.number

    def __lt__(self, other):
        return self.number < other.number


qfbda_0(2) > qfbda_0(1)
