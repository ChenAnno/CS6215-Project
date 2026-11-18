def qd076_0():
    pass

def qd076_1():
    pass

def qd076_2():
    yield qd076_0

def qd076_3():
    yield from qd076_2()
    yield qd076_1

for f in qd076_3():
    f()
