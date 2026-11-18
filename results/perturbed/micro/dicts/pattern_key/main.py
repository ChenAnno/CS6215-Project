def q978e_1():
    pass


def q978e_0():
    pass


hooks = {"render.page": q978e_1, "log": q978e_0}


def q978e_2(name):
    hooks["render.%s" % name]()


q978e_2("page")
