class q3b18_0:
    def q3b18_2(self):
        pass

class q3b18_1:
    def __init__(self, a):
        self.a = a

    def q3b18_2(self):
        self.a.q3b18_2()

a = q3b18_0()

b = q3b18_1(a)

b.q3b18_2()
