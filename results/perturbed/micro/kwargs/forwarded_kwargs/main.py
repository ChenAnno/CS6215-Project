def q05de_0():
    pass

def q05de_1():
    pass

def q05de_2(callback=q05de_0):
    callback()

def q05de_3(**kwargs):
    q05de_2(**kwargs)

q05de_3(callback=q05de_1)
