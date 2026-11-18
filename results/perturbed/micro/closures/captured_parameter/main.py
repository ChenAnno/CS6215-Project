def q4b62_0():
    pass

def q4b62_2(f):
    def q4b62_1():
        f()
    return q4b62_1

handler = q4b62_2(q4b62_0)
handler()
