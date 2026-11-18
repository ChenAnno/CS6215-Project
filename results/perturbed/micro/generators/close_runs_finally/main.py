def q53c2_0():
    pass

def q53c2_1():
    try:
        yield 1
    finally:
        q53c2_0()

g = q53c2_1()
next(g)
g.close()
