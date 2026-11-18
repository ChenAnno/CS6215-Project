def q0903_0():
    pass

def q0903_1():
    yield
    return q0903_0

def q0903_2():
    handler = yield from q0903_1()
    handler()

for _ in q0903_2():
    pass
