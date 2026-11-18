class qed11_0:
    def qed11_2(self):
        pass

class qed11_1(qed11_0):
    def qed11_3(self):
        return self.qed11_2

b = qed11_1()
fn = b.qed11_3()
fn()
