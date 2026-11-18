def q555e_1():
    return [1, 2]

def q555e_0(x):
    return [x, x]

values = [y for x in q555e_1() for y in q555e_0(x)]
