from typing import overload


def q9b75_0(value):
    return value


@overload
def q9b75_1(value: int) -> int: ...


@overload
def q9b75_1(value: str) -> str: ...


def q9b75_1(value):
    return q9b75_0(value)


q9b75_1(1)
