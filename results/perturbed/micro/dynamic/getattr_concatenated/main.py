class q7b6e_0:
    def q7b6e_3(self):
        pass

    def q7b6e_2(self):
        pass

def q7b6e_1(handler, event):
    getattr(handler, "on_" + event)()

q7b6e_1(q7b6e_0(), "close")
