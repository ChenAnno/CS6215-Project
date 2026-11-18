def q1b24_2():
    pass


class q1b24_1:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class q1b24_0(q1b24_1):
    def __exit__(self, *args):
        q1b24_2()


with q1b24_0():
    pass
