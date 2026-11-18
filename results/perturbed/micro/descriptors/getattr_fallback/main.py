def q2355_1():
    pass


class q2355_0:
    def q2355_2(self):
        pass

    def __getattr__(self, name):
        return q2355_1


def q2355_3(proxy):
    proxy.q2355_2()


def q2355_4(proxy):
    proxy.missing()


proxy = q2355_0()
q2355_3(proxy)
q2355_4(proxy)
