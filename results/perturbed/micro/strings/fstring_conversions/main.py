class q134c_0:
    def __str__(self):
        return "str"

    def __repr__(self):
        return "repr"

    def __format__(self, spec):
        return "format"

v = q134c_0()
message = f"{v!s} {v!r} {v}"
