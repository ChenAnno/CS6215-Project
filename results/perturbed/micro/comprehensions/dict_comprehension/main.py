def qf414_2(f):
    return f.__name__

def qf414_0():
    return 1

def qf414_1():
    return 2

results = {qf414_2(f): f() for f in (qf414_0, qf414_1)}
