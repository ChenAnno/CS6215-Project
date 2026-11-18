import json

class q295b_0(json.JSONEncoder):
    def q295b_1(self, value):
        return sorted(value)

def q295b_3():
    json.dumps({"b", "a"}, cls=q295b_0)

def q295b_2():
    json.dumps([1, 2], cls=q295b_0)

q295b_3()
q295b_2()
