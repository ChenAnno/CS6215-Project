from typing import AbstractSet, Iterator

class qbadd_0(Iterator):
    def __next__(self):
        raise StopIteration

class qbadd_1(AbstractSet):
    def __contains__(self, item):
        return False

    def __iter__(self):
        yield from ()

    def __len__(self):
        return 0

qbadd_0().__iter__()
qbadd_1().isdisjoint(())
