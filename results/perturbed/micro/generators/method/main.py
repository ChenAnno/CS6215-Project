def q7018_2():
    pass

def q7018_3():
    pass

class q7018_0:
    def __init__(self):
        self.handlers = [q7018_2, q7018_3]

    def q7018_1(self):
        for h in self.handlers:
            yield h

registry = q7018_0()
for h in registry.q7018_1():
    h()
