class qc0a3_0(object):
    def __init__(self, n):
        self.n = n
        self.num = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.num < self.n:
            cur, self.num = self.num, self.num + 1
            return cur
        else:
            raise StopIteration()

for i in qc0a3_0(100):
    pass
