class q6096_0:
    def __getitem__(self, index):
        if index < 2:
            return index
        raise IndexError(index)


for item in q6096_0():
    pass
