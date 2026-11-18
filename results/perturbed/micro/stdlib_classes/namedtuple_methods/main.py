from collections import namedtuple


class Point(namedtuple("Point", "x y")):
    def qf9d7_0(self):
        return abs(self.x) + abs(self.y)


Point(1, -2).qf9d7_0()
