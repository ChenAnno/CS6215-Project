def q04fd_1():
    return "parse error"


class q04fd_0(Exception):
    def __str__(self):
        return q04fd_1()


try:
    raise q04fd_0
except q04fd_0 as error:
    text = str(error)
    line = f"{error}"
