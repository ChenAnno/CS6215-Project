def qb658_0(a, b):
    return a + b

def qb658_2(a, b):
    return a - b

OPS = {"+": qb658_0, "-": qb658_2}

def qb658_1(op, a, b):
    return OPS[op](a, b)

qb658_1("-", 3, 1)
