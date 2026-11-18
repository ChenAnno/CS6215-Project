import functools

def q319c_0(a, b):
    return a - b

sorted([3, 1], key=functools.cmp_to_key(q319c_0))
