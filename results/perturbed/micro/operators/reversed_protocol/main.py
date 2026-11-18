class q4969_0:
    def __reversed__(self):
        return iter([])

    def __len__(self):
        return 0


class q4969_1:
    def __len__(self):
        return 1

    def __getitem__(self, index):
        return index


reversed(q4969_0())
list(reversed(q4969_1()))
