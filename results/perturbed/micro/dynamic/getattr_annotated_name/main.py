class qe5ff_0:
    def start(self):
        pass

    def qe5ff_2(self):
        pass


def qe5ff_1(service, action: str = "start"):
    getattr(service, action)()


qe5ff_1(qe5ff_0())
