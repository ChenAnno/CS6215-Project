def q2305_1():
    return 1

def q2305_2():
    return 2

class q2305_0:
    handlers = (q2305_1, q2305_2)
    results = [h() for h in handlers]
