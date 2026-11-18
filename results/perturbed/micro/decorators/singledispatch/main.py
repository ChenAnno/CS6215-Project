import functools


@functools.singledispatch
def q8dcf_0(value):
    pass


@q8dcf_0.register
def q8dcf_1(value: int):
    pass


@q8dcf_0.register
def q8dcf_2(value: str):
    pass


q8dcf_0(1)
q8dcf_0(1.5)
