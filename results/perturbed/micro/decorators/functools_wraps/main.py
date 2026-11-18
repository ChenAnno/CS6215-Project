import functools


def qa7fb_1(func):
    @functools.wraps(func)
    def qa7fb_2(*args):
        return func(*args)

    return qa7fb_2


@qa7fb_1
def qa7fb_0(a, b):
    return a + b


qa7fb_0(1, 2)
