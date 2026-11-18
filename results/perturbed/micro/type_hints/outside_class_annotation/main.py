import collections.abc
import pickle


class qb47f_0(collections.abc.Iterator):
    def __init__(self):
        self.left = 2

    def __next__(self):
        if self.left == 0:
            raise StopIteration
        self.left -= 1
        return self.left


class qb47f_1:
    def __iter__(self):
        return self

    def __next__(self):
        raise StopIteration


def qb47f_2(numbers: collections.abc.Iterator) -> None:
    for number in numbers:
        pass


qb47f_2(pickle.loads(pickle.dumps(qb47f_0())))
