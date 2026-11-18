def q3323_0():
    pass

def q3323_1():
    pass

def q3323_2(f, registry=[]):
    registry.append(f)
    return registry

q3323_2(q3323_0)
for f in q3323_2(q3323_1):
    f()
