def q1d66_0():
    pass

def q1d66_1():
    pass

handler = q1d66_0

def q1d66_2():
    global handler
    handler = q1d66_1

q1d66_2()
handler()
