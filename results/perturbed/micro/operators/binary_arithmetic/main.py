class qb8ee_0:
    def __add__(self, other):
        return self

    def __sub__(self, other):
        return self

    def __matmul__(self, other):
        return 0


v = qb8ee_0()
w = v + v
d = v @ w
