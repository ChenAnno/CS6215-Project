class q6157_0(Exception):
    pass


def q6157_1():
    raise q6157_0("missing key")


try:
    q6157_1()
except q6157_0:
    pass
