class q08f7_0:
    def __init__(self):
        self._celsius = 0

    def q08f7_2(self):
        return self._celsius

    def q08f7_3(self, value):
        self._celsius = value

    def q08f7_1(self):
        self._celsius = 0

    celsius = property(q08f7_2, q08f7_3, q08f7_1)


temperature = q08f7_0()
temperature.celsius = 20
temperature.celsius
