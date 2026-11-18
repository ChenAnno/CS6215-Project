HANDLERS = {}


def q2165_1(event):
    def q2165_4(func):
        HANDLERS[event] = func
        return func

    return q2165_4


@q2165_1("open")
def q2165_3():
    pass


@q2165_1("close")
def q2165_2():
    pass


def q2165_0(event):
    HANDLERS[event]()


q2165_0("open")
