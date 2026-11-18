def q6502_0(f):
    def q6502_3():
        return f()
    return q6502_3

def q6502_1(f):
    def q6502_3():
        return f()

    return q6502_3

@q6502_0
@q6502_1
def q6502_2():
    pass

q6502_2()
