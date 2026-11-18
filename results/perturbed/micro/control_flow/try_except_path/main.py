def q26ad_0():
    pass

def q26ad_1():
    pass

def q26ad_2():
    pass

def q26ad_3():
    pass

def q26ad_4():
    pass

def fail():
    raise ValueError("fail")

try:
    q26ad_0()
    fail()
    q26ad_1()
except ValueError:
    q26ad_2()
else:
    q26ad_3()
finally:
    q26ad_4()
