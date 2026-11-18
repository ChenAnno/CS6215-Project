class q7f9a_0:
    def q7f9a_2(self):
        return True

    def q7f9a_3(self):
        pass


def q7f9a_1(task):
    return task.q7f9a_2()


for task in filter(q7f9a_1, [q7f9a_0()]):
    task.q7f9a_3()
