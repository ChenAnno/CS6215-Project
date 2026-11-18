def qf55a_0():
    return 1

def qf55a_1():
    result = None
    while True:
        task = yield result
        result = task()

g = qf55a_1()
next(g)
g.send(qf55a_0)
