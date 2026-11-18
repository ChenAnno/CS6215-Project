class qc72e_0:
    def __iadd__(self, other):
        return self

    def __add__(self, other):
        return self


class qc72e_1:
    def __add__(self, other):
        return self


buffer = qc72e_0()
buffer += 1
counter = qc72e_1()
counter += 1
