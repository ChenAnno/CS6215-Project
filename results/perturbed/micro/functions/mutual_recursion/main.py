def qf231_0(n):
    if n == 0:
        return True
    return qf231_1(n - 1)

def qf231_1(n):
    if n == 0:
        return False
    return qf231_0(n - 1)

qf231_0(4)
