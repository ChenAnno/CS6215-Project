class qbf44_0:
    def qbf44_2(self):
        pass


class qbf44_1(qbf44_0):
    def qbf44_2(self):
        call_parent = lambda obj: super().qbf44_2()
        call_parent(self)


qbf44_1().qbf44_2()
