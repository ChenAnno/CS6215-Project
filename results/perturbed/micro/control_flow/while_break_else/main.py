def q64ff_0():
    pass

def q64ff_1():
    pass

def q64ff_2():
    pass

handlers = [q64ff_0, q64ff_1]
i = 0
while i < 2:
    handlers[i]()
    if handlers[i] is q64ff_0:
        break
    i += 1
else:
    q64ff_2()
