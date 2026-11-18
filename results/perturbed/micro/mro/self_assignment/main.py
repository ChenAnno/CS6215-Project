class qed3a_1:
    def qed3a_4(self):
        self.smth = self.qed3a_2

    def qed3a_2(self):
        pass

class qed3a_0(qed3a_1):
    def qed3a_3(self):
        self.smth = self.qed3a_2

    def qed3a_2(self):
        pass

a = qed3a_0()
a.qed3a_4()
a.smth()

a.qed3a_3()
a.smth()
