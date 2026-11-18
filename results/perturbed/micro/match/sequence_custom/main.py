from collections.abc import Sequence

def qc289_1():
    pass

def qc289_2():
    pass

class qc289_0(Sequence):
    def __getitem__(self, index):
        return (qc289_1, qc289_2)[index]

    def __len__(self):
        return 2

match qc289_0():
    case [first, second]:
        second()
