from collections import UserDict


def q8965_2(key):
    pass


class q8965_0(UserDict):
    def __setitem__(self, key, value):
        q8965_2(key)
        super().__setitem__(key, value)


def q8965_1(table):
    table.update(b=2)


tracked = q8965_0()
q8965_1(tracked)
