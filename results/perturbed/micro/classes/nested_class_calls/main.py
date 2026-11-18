class q9c4c_2:
    def q9c4c_3(self):
        pass

class q9c4c_1:
    def __init__(self, c):
        self.c = c

    def q9c4c_3(self):
        self.c.q9c4c_3()

class q9c4c_0:
    def __init__(self):
        self.c = q9c4c_2()

    def q9c4c_3(self):
        b = q9c4c_1(self.c)
        b.q9c4c_3()

a = q9c4c_0()
a.q9c4c_3()
