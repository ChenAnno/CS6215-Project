def qdf7b_0(f):
    def qdf7b_3():
        f()

    return qdf7b_3

@qdf7b_0
def qdf7b_1():
    pass

def qdf7b_2():
    qdf7b_1()

qdf7b_2()
