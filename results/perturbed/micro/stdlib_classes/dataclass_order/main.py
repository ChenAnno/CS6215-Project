from dataclasses import dataclass


class q09bd_0:
    def __init__(self, number):
        self.number = number

    def __eq__(self, other):
        return self.number == other.number

    def __lt__(self, other):
        return self.number < other.number


@dataclass(order=True)
class q09bd_1:
    part: q09bd_0


sorted([q09bd_1(q09bd_0(2)), q09bd_1(q09bd_0(1))])
