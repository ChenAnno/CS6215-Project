def q0264_1():
    pass

class q0264_0:
    __match_args__ = ("action",)

    @property
    def action(self):
        return q0264_1

match q0264_0():
    case q0264_0(handler):
        handler()
