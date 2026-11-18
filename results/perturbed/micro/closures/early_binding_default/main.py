def qad5f_1():
    pass

def qad5f_2():
    pass

def qad5f_0():
    handlers = []
    for f in (qad5f_1, qad5f_2):
        handlers.append(lambda f=f: f())
    return handlers

qad5f_0()[0]()
