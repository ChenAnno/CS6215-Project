class q0360_0:
    def __str__(self):
        return "str"

    def __repr__(self):
        return "repr"


def q0360_1(node):
    message = "%r is its own parent"
    return message % (node,)


q0360_1(q0360_0())
