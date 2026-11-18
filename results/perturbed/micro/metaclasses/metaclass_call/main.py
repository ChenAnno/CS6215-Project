class q2090_1(type):
    def __call__(cls, *args):
        if not hasattr(cls, "instance"):
            cls.instance = super().__call__(*args)
        return cls.instance


class q2090_0(metaclass=q2090_1):
    def __init__(self):
        pass


q2090_0()
q2090_0()
