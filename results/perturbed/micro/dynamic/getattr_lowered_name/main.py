class q8bff_0:
    pass


class q8bff_1:
    pass


class q8bff_2:
    pass


class q8bff_3:
    def visit(self, node):
        name = f"visit_{type(node).__name__}".lower()
        method = getattr(self, name, self.q8bff_4)
        return method(node)

    def q8bff_4(self, node):
        pass

    def q8bff_6(self, node):
        pass

    def q8bff_5(self, node):
        pass

    def q8bff_7(self, node):
        pass


visitor = q8bff_3()
visitor.visit(q8bff_0())
visitor.visit(q8bff_1())
visitor.visit(q8bff_2())
