def qec28_1():
    pass

def qec28_2():
    pass

def qec28_0(subject):
    match subject:
        case [first, second]:
            return qec28_1
        case _:
            return qec28_2

qec28_0("ab")()
