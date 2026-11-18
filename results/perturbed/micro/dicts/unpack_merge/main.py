def qe254_0():
    pass

def qe254_1():
    pass

defaults = {"run": qe254_0}
overrides = {"run": qe254_1}
merged = {**defaults, **overrides}
merged["run"]()
