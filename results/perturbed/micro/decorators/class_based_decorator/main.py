class q8460_0:
    def __init__(self, func):
        self.func = func
        self.calls = 0

    def __call__(self, *args):
        self.calls += 1
        return self.func(*args)


@q8460_0
def q8460_1(name):
    pass


q8460_1("a")
