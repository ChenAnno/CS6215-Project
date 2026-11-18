class q283d_1:
    def q283d_2(self):
        return "text"


class q283d_0:
    def q283d_2(self):
        return "image"


def q283d_3(item):
    if not isinstance(item, q283d_1):
        return item.q283d_2()
    return "plain"


q283d_3(q283d_1())
q283d_3(q283d_0())
