def q1596_1():
    pass

def q1596_2():
    pass

class q1596_0:
    __match_args__ = ("action",)

    def __init__(self, action, fallback):
        self.action = action
        self.fallback = fallback

match q1596_0(q1596_1, q1596_2):
    case q1596_0(action, fallback=other):
        action()
