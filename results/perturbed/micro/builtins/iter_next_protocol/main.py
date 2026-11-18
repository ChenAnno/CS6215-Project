class q7918_0:
    def __iter__(self):
        return self

    def __next__(self):
        return 1

iterator = iter(q7918_0())
next(iterator)
