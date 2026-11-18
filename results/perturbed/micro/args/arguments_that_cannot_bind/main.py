class qa91a_1:
    def __init__(self):
        pass


class qa91a_0:
    def __init__(self, name):
        pass


def qa91a_2(kind):
    try:
        return kind()
    except TypeError:
        return None


for kind in (qa91a_1, qa91a_0):
    qa91a_2(kind)
