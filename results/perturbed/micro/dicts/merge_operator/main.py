def q3c4f_0():
    pass

def q3c4f_1():
    pass

defaults = {"run": q3c4f_0}
overrides = {"run": q3c4f_1}
(defaults | overrides)["run"]()
