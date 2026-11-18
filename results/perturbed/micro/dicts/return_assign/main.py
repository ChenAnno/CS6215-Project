def qfbbc_1():
    pass

def qfbbc_0():
    return qfbbc_1

d = {"a": qfbbc_0()}

d["a"]()
