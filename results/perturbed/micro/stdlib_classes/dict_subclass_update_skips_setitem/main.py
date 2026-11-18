def qa32f_3(key):
    pass


class qa32f_0(dict):
    def __setitem__(self, key, value):
        qa32f_3(key)
        super().__setitem__(key, value)


def qa32f_1(table):
    table["a"] = 1


def qa32f_2(table):
    table.update(b=2)


tracked = qa32f_0()
qa32f_1(tracked)
qa32f_2(tracked)
