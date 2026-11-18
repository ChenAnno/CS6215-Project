def qbc33_0():
    pass

def qbc33_1():
    pass

handlers = [lambda: g() for g in (qbc33_0, qbc33_1)]
handlers[0]()
