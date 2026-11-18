class q7d22_0:
    def __init__(self, name):
        self.name = name

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name


table = {q7d22_0("a"): 1}
table[q7d22_0("a")]
