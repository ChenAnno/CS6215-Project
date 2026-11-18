def q466f_0():
    pass

def q466f_1():
    pass

def q466f_2():
    pass

handler = q466f_0
for following in (q466f_1, q466f_2):
    handler()
    handler = following
