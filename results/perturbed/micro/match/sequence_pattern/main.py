def qec31_0():
    pass

def qec31_1():
    pass

def qec31_2():
    pass

match (qec31_0, qec31_1, qec31_2):
    case [first, *rest]:
        rest[-1]()
