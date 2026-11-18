class q7297_3:
    def q7297_4(self):
        pass


class q7297_1(q7297_3):
    def q7297_4(self):
        super().q7297_4()


class q7297_2(q7297_3):
    def q7297_4(self):
        pass


class q7297_0(q7297_1, q7297_2):
    pass


q7297_1().q7297_4()
