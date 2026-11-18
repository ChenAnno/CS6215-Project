def q9487_0():
    return 1

def q9487_1():
    return 2

total = sum(f() for f in (q9487_0, q9487_1))
