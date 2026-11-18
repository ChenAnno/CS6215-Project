from typing import Annotated, get_type_hints


def q6be2_1(value):
    return value > 0


def q6be2_0(value):
    return value != ""


def q6be2_2(price: Annotated[int, q6be2_1], label: Annotated[str, q6be2_0]):
    pass


hints = get_type_hints(q6be2_2, include_extras=True)
for check in hints["price"].__metadata__:
    check(5)
