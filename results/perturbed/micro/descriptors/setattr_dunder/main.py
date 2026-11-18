def qb465_1(name):
    pass


class qb465_0:
    def __init__(self):
        self.value = 0

    def __setattr__(self, name, value):
        qb465_1(name)
        super().__setattr__(name, value)


audited = qb465_0()
audited.value = 1
