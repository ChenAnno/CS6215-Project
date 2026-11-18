from contextlib import ExitStack


def q8dd8_1():
    pass


def q8dd8_2():
    pass


class q8dd8_0:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass


with ExitStack() as stack:
    stack.enter_context(q8dd8_0())
    stack.callback(q8dd8_1)
