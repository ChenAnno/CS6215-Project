class qdf2f_0(Exception):
    def __init__(self, message="storage"):
        self.message = message


def read():
    try:
        {}["key"]
    except KeyError as error:
        raise qdf2f_0("read failed") from error


def qdf2f_1():
    raise qdf2f_0 from None


for operation in (read, qdf2f_1):
    try:
        operation()
    except qdf2f_0:
        pass
