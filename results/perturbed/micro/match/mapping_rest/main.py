def qb865_0():
    pass

def qb865_1():
    pass

config = {"on_start": qb865_0, "on_stop": qb865_1}
match config:
    case {"on_start": handler, **rest}:
        rest["on_stop"]()
