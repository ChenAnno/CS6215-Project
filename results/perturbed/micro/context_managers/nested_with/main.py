class q7642_1:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def q7642_2(self):
        pass


class q7642_0:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def q7642_3(self):
        return q7642_1()


with q7642_0() as db:
    with db.q7642_3() as tx:
        tx.q7642_2()
