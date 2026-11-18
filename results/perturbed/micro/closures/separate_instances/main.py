def q2342_0():
    pass

def q2342_1():
    pass

def q2342_3(f):
    def q2342_2():
        f()
    return q2342_2

first = q2342_3(q2342_0)
second = q2342_3(q2342_1)
first()
