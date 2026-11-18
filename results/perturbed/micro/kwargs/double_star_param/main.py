def q5302_0():
    pass

def q5302_1():
    pass

def q5302_2(**handlers):
    handlers["second"]()

q5302_2(first=q5302_0, second=q5302_1)
