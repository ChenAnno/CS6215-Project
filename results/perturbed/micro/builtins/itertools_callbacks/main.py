import itertools

def q7b28_0(a, b):
    return a * b

def q7b28_2(n):
    return n < 3

def q7b28_1(n):
    return n % 2

list(itertools.starmap(q7b28_0, [(1, 2), (3, 4)]))
list(itertools.takewhile(q7b28_2, [1, 5, 2]))
list(itertools.groupby([1, 3, 2], key=q7b28_1))
