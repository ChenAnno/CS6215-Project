def q7fed_0():
    return True

def q7fed_1():
    return False

results = (f() for f in (q7fed_0, q7fed_1))
found = any(results)
