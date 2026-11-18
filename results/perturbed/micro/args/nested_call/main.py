def qa609_1():
    pass

def qa609_2(a):
    a()

def qa609_0(a):
    a(qa609_1)

b = qa609_2
c = qa609_0
c(b)
