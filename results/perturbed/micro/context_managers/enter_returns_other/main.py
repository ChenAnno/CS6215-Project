class q3691_0:
    def q3691_2(self):
        pass


class q3691_1:
    def __enter__(self):
        return q3691_0()

    def __exit__(self, *args):
        pass

    def q3691_2(self):
        pass


with q3691_1() as conn:
    conn.q3691_2()
