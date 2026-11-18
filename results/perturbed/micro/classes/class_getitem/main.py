def q33c1_1(key):
    pass


class q33c1_0:
    def __class_getitem__(cls, key):
        return q33c1_1(key)


q33c1_0["audio"]
