def q8eef_3():
    pass

def q8eef_2():
    pass

def q8eef_0(f):
    return f is not q8eef_3

def q8eef_1(handler):
    match handler:
        case f if q8eef_0(f):
            return f
        case _:
            return q8eef_2

q8eef_1(q8eef_3)()
