class qca2d_0:
    def __getitem__(self, key):
        return 0

    def __setitem__(self, key, value):
        pass


counter = qca2d_0()
counter["a"] += 1
