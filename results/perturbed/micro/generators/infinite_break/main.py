def q8898_1():
    pass

def q8898_2():
    pass

def q8898_0():
    while True:
        yield q8898_1
        yield q8898_2

for f in q8898_0():
    f()
    break
