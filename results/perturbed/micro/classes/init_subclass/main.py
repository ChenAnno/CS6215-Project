class q37a9_1:
    registry = []

    def __init_subclass__(cls):
        super().__init_subclass__()
        cls.registry.append(cls)


class q37a9_0(q37a9_1):
    pass


class q37a9_2(q37a9_1):
    pass
