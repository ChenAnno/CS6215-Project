def q9b04_2():
    return 0


class q9b04_0(dict):
    def __missing__(self, key):
        return q9b04_2()


def q9b04_1(table):
    return table["a"]


def q9b04_3(table):
    return table.get("b")


table = q9b04_0()
q9b04_1(table)
q9b04_3(table)
