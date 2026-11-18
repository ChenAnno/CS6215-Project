class q4a41_0:
    def __set_name__(self, owner, name):
        self.name = "_" + name

    def __get__(self, obj, objtype=None):
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        setattr(obj, self.name, value)


class q4a41_1:
    email = q4a41_0()


user = q4a41_1()
user.email = "a"
user.email
