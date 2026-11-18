def qecae_1():
    pass

def qecae_0(n):
    num = 0
    while num < n:
        yield qecae_1
        num += 1

for i in qecae_0(100):
    i()
