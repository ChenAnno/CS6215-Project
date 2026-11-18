def q132f_0():
    pass

def q132f_1(f):
    def q132f_2():
        f()
    return q132f_2

wrapped = q132f_1(q132f_1(q132f_0))
wrapped()
