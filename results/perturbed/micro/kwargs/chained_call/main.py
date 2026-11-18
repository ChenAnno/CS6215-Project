def q9dc2_2():
    pass

def q9dc2_1(a=q9dc2_2):
    a()

def q9dc2_0(a, b=q9dc2_1):
    a(b)

q9dc2_0(a=q9dc2_1, b=q9dc2_2)
