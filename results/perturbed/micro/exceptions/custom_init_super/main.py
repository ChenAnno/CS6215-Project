class q0358_0(Exception):
    def __init__(self, code):
        super().__init__(f"code {code}")
        self.code = code


try:
    raise q0358_0(3)
except q0358_0:
    pass
