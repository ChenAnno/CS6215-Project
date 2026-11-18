def q8e81_0():
    pass

def q8e81_1():
    pass

config = {"on_start": q8e81_0, "on_stop": q8e81_1}
match config:
    case {"on_stop": handler}:
        handler()
