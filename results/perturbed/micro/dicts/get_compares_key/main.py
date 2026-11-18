class q9f72_0:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


table = {q9f72_0("a"): 1}
table.get(q9f72_0("a"))
