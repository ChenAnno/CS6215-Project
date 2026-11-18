def q5bd3_0():
    pass

def q5bd3_1():
    pass

def q5bd3_2():
    yield q5bd3_0
    yield q5bd3_1

first, second = q5bd3_2()
second()
