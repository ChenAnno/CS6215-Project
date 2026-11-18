def qd36a_1():
    return False


def qd36a_0():
    return "not empty"


try:
    assert qd36a_1(), qd36a_0()
except AssertionError:
    pass
