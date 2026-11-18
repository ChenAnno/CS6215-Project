import functools
import operator


class qc895_0:
    def __add__(self, other):
        return self

    def __getitem__(self, index):
        return 0


v = qc895_0()
operator.add(v, v)
operator.getitem(v, 0)
functools.reduce(operator.add, [v, v])
