def q4f12_2(name):
    def q4f12_0(func):
        def q4f12_3():
            return func()

        return q4f12_3

    return q4f12_0


@q4f12_2("outer")
@q4f12_2("inner")
def q4f12_1():
    pass


q4f12_1()
