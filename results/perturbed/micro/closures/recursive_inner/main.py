def qf328_1():
    pass

def qf328_2(n):
    def qf328_0(k):
        if k > 0:
            qf328_0(k - 1)
        else:
            qf328_1()

    qf328_0(n)

qf328_2(2)
