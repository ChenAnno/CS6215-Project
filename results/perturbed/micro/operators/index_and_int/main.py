class qbd9e_1:
    def __index__(self):
        return 1


class qbd9e_0:
    def __int__(self):
        return 5

    def __float__(self):
        return 5.0


items = ["a", "b"]
items[qbd9e_1()]
range(qbd9e_1())
int(qbd9e_0())
float(qbd9e_0())
