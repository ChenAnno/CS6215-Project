import ext

def qd10a_0():
    pass

try:
    raise ext.Error("failed")
except ext.Error:
    qd10a_0()
