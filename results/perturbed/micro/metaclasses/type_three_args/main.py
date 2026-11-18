def greet(self):
    pass


class q8188_0:
    def __init__(self):
        pass


Dynamic = type("Dynamic", (q8188_0,), {"greet": greet})
Dynamic().greet()
