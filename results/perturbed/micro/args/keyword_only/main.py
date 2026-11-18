def q1fa0_0():
    pass

def q1fa0_1():
    pass

def q1fa0_2(*, first, second):
    second()

q1fa0_2(second=q1fa0_1, first=q1fa0_0)
