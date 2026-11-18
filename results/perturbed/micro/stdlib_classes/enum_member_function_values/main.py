from enum import Enum, member


def qc8f2_1(a, b):
    return a + b


def qc8f2_3(a, b):
    return a - b


class qc8f2_0(Enum):
    ADD = member(qc8f2_1)
    SUBTRACT = member(qc8f2_3)

    def qc8f2_2(self, a, b):
        return self.value(a, b)


qc8f2_0.ADD.qc8f2_2(1, 2)
