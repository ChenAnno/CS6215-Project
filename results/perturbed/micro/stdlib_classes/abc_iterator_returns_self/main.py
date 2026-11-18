from collections.abc import Iterator

def q2980_1():
    pass

class q2980_0(Iterator):
    def __init__(self):
        self.left = 1

    def __next__(self):
        if self.left == 0:
            raise StopIteration
        self.left -= 1
        return q2980_1

for handler in q2980_0():
    handler()
