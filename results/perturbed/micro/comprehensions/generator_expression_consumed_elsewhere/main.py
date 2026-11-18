def q485f_1():
    return 1

def q485f_2():
    return 2

def q485f_0(values):
    total = 0
    for v in values:
        total += v
    return total

q485f_0(f() for f in (q485f_1, q485f_2))
