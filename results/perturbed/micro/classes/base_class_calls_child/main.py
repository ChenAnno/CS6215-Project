class qac4a_0:
    def qac4a_3(self):
        self.child()

class qac4a_1(qac4a_0):
    def __init__(self):
        self.child = self.qac4a_4

    def qac4a_4(self):
        pass

class qac4a_2(qac4a_0):
    def __init__(self):
        self.child = self.qac4a_4

    def qac4a_4(self):
        pass

b = qac4a_1()
b.qac4a_3()

c = qac4a_2()
c.qac4a_3()
