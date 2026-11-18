class qbd12_0(type):
    def __getitem__(cls, key):
        return key


class qbd12_1(metaclass=qbd12_0):
    def __class_getitem__(cls, key):
        return key


qbd12_1["red"]
