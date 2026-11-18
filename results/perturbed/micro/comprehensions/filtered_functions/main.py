def q0ff5_0():
    pass

def q0ff5_1():
    pass

def q0ff5_2():
    pass

handlers = [f for f in (q0ff5_0, q0ff5_1, q0ff5_2) if f is not q0ff5_1]
for h in handlers:
    h()
