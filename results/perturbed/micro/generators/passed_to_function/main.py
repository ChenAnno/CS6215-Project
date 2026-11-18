def q468c_1():
    pass

def q468c_2():
    yield q468c_1

def q468c_0(handlers):
    for h in handlers:
        h()

q468c_0(q468c_2())
