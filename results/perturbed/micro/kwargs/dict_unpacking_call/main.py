def qe990_0():
    pass

def qe990_1():
    pass

def qe990_2(f, g):
    f()

options = {"g": qe990_1, "f": qe990_0}
qe990_2(**options)
