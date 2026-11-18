def q9056_0():
    pass

def q9056_1():
    pass

def q9056_2():
    pass

def q9056_3():
    pass

def q9056_4():
    pass

def q9056_5(a, /, b, *args, c, **kwargs):
    a()
    b()
    args[0]()
    c()
    kwargs["d"]()

q9056_5(q9056_0, q9056_1, q9056_2, c=q9056_3, d=q9056_4)
