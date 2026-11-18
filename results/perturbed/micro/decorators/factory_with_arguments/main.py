def qc5f1_2(times):
    def qc5f1_0(func):
        def qc5f1_3():
            for _ in range(times):
                func()

        return qc5f1_3

    return qc5f1_0


@qc5f1_2(2)
def qc5f1_1():
    pass


qc5f1_1()
