def qc40b_0():
    pass

def qc40b_1():
    pass

ops = {
    "first": lambda: qc40b_0(),
    "second": lambda: qc40b_1(),
}
ops["second"]()
