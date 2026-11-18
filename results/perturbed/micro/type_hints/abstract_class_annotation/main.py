import collections.abc
import pickle


class q7e9f_0(collections.abc.Sequence):
    def __getitem__(self, index):
        if index >= 2:
            raise IndexError
        return index

    def __len__(self):
        return 2


class q7e9f_1:
    def __getitem__(self, index):
        raise IndexError

    def __len__(self):
        return 0


def q7e9f_2(numbers: collections.abc.Sequence) -> None:
    numbers[0]
    len(numbers)


q7e9f_2(pickle.loads(pickle.dumps(q7e9f_0())))
