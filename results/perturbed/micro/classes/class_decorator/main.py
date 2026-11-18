registry = []


def q667b_1(cls):
    registry.append(cls)
    return cls


@q667b_1
class q667b_0:
    def __init__(self):
        pass


for plugin_class in registry:
    plugin_class()
