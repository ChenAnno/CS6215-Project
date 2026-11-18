class qedca_0:
    def __hash__(self):
        return 1

    def __eq__(self, other):
        return True


key = qedca_0()
table = {key: 1}
table[key]
