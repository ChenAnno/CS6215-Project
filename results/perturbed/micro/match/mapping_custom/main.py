from collections.abc import Mapping

def qe02d_1():
    pass

class qe02d_0(Mapping):
    def __getitem__(self, key):
        return qe02d_1

    def __iter__(self):
        return iter(["run"])

    def __len__(self):
        return 1

match qe02d_0():
    case {"run": handler}:
        handler()
