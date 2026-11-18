class q2ae7_0:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


class q2ae7_1:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


with q2ae7_0("a") as lock, q2ae7_1() as timer:
    pass
