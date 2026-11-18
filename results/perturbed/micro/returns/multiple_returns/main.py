def qb6d5_0():
    pass

def qb6d5_1():
    pass

def qb6d5_2(first):
    if first:
        return qb6d5_0
    return qb6d5_1

qb6d5_2(False)()
