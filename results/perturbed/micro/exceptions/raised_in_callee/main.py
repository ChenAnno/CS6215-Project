def q3524_0():
    pass


def q3524_2():
    pass


def q3524_1():
    raise PermissionError("denied")
    q3524_0()


def q3524_3():
    try:
        q3524_1()
    except PermissionError:
        q3524_2()


q3524_3()
