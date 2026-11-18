def qbb8b_1():
    pass

def qbb8b_0():
    pass

handlers = [qbb8b_1, qbb8b_0]
handlers.sort(key=lambda f: f.__name__)
handlers[0]()
