def q392e_0():
    pass

def q392e_1():
    pass

first = lambda: q392e_0()
gen = (lambda: q392e_1() for _ in range(1))
second = next(gen)
second()
first()
