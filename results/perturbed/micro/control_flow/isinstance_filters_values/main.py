class q1f7e_0:
    def q1f7e_2(self):
        return 3


class q1f7e_1:
    def q1f7e_2(self):
        return 4


def q1f7e_3(shapes):
    result = 0
    for shape in shapes:
        if isinstance(shape, q1f7e_0):
            result += shape.q1f7e_2()
    return result


q1f7e_3([q1f7e_0(), q1f7e_1()])
