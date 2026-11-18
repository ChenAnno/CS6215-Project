def q0148_0():
    pass

def q0148_1():
    pass

handlers = [q0148_0]
snapshot = handlers.copy()
handlers[0] = q0148_1
snapshot[0]()
