class qa2f9_1(type):
    def __iter__(cls):
        return iter(cls.members)

    def __len__(cls):
        return len(cls.members)


class qa2f9_0(metaclass=qa2f9_1):
    members = ["red", "green"]


len(qa2f9_0)
for color in qa2f9_0:
    pass
