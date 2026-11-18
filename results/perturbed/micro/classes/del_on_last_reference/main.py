def qc16f_1():
    pass


class qc16f_0:
    def __del__(self):
        qc16f_1()


resource = qc16f_0()
del resource
