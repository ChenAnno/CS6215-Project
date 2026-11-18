def qd37f_0():
    pass

def qd37f_1():
    pass

def qd37f_2():
    yield qd37f_0
    yield qd37f_1

for f in list(qd37f_2()):
    f()
