def qff1a_3(x):
    return x + 1

def qff1a_2(x):
    return x * 2

def qff1a_0(f, g):
    def qff1a_1(x):
        return f(g(x))
    return qff1a_1

qff1a_0(qff1a_3, qff1a_2)(3)
