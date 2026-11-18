from enum import Enum


class q8d8a_0(Enum):
    ACTIVE = "active"
    UNKNOWN = "unknown"

    @classmethod
    def q8d8a_1(cls, value):
        return cls.UNKNOWN


def q8d8a_2():
    return q8d8a_0("active")


def q8d8a_3():
    return q8d8a_0("deleted")


q8d8a_2()
q8d8a_3()
