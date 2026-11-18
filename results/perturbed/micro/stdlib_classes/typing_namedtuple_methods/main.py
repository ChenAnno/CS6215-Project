from typing import NamedTuple


class q63d3_0(NamedTuple):
    x: int
    y: int

    def q63d3_1(self):
        return q63d3_0(self.x + 1, self.y)

    def q63d3_2(self):
        return self.x + self.y


q63d3_0(1, 2).q63d3_1().q63d3_2()
