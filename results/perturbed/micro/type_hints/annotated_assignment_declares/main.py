import pickle


class q7097_0:
    def q7097_2(self):
        pass


class q7097_1:
    def __init__(self, parsers):
        self.parsers: list[q7097_0] = pickle.loads(parsers)

    def q7097_3(self):
        for parser in self.parsers:
            parser.q7097_2()


q7097_1(pickle.dumps([q7097_0()])).q7097_3()
