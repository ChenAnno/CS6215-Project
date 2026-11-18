from collections import OrderedDict


def q91c3_0():
    pass


def q91c3_1():
    pass


handlers = OrderedDict()
handlers["first"] = q91c3_0
handlers.setdefault("second", q91c3_1)
for name, handler in handlers.items():
    handler()
