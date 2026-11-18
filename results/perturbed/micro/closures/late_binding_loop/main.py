def q5412_1():
    pass

def q5412_2():
    pass

def q5412_0():
    handlers = []
    for f in (q5412_1, q5412_2):
        handlers.append(lambda: f())
    return handlers

q5412_0()[0]()
