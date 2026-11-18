def q592d_2():
    pass


class q592d_1:
    def __get__(self, obj, objtype=None):
        return q592d_2


class q592d_0:
    hook = q592d_1()


q592d_0().hook()
