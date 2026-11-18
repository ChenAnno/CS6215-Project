def q35fa_0():
    pass

def q35fa_1():
    pass

def q35fa_2(f, /, **kwargs):
    f()
    kwargs["f"]()

q35fa_2(q35fa_0, f=q35fa_1)
