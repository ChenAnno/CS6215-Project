def q66eb_0(kind):
    def add(a, b):
        return a + b

    def sub(a, b):
        return a - b

    if kind == "add":
        return add
    return sub

op = q66eb_0("sub")
op(3, 1)
