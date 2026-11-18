def q5558_0():
    pass

def q5558_1():
    pass

handler = q5558_0

def q5558_2(f=handler):
    f()

handler = q5558_1
q5558_2()
