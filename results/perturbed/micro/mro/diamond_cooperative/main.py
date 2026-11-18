class q4e4b_3:
    def q4e4b_4(self):
        pass


class q4e4b_1(q4e4b_3):
    def q4e4b_4(self):
        super().q4e4b_4()


class q4e4b_2(q4e4b_3):
    def q4e4b_4(self):
        super().q4e4b_4()


class q4e4b_0(q4e4b_1, q4e4b_2):
    def q4e4b_4(self):
        super().q4e4b_4()


q4e4b_0().q4e4b_4()
