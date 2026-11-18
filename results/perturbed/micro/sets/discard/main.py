def q34d7_0():
    pass

def q34d7_1():
    pass

handlers = {q34d7_0, q34d7_1}
handlers.discard(q34d7_0)
for f in handlers:
    f()
