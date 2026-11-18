def qc7b8_0():
    pass

def qc7b8_1():
    pass

def qc7b8_2(first, second=None):
    first()
    second()

def qc7b8_3(*args, **kwargs):
    qc7b8_2(*args, **kwargs)

qc7b8_3(qc7b8_0, second=qc7b8_1)
