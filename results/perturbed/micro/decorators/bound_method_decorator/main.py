class q800e_0:
    def __init__(self):
        self.items = []

    def q800e_1(self, func):
        self.items.append(func)
        return func


registry = q800e_0()


@registry.q800e_1
def q800e_2():
    pass


for item in registry.items:
    item()
