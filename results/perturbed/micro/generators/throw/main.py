def qcf0c_1():
    pass

def qcf0c_0():
    try:
        yield 1
    except ValueError:
        qcf0c_1()
        yield 2

g = qcf0c_0()
next(g)
g.throw(ValueError)
