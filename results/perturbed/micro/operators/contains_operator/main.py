class q736a_0:
    def __contains__(self, item):
        return True

    def __iter__(self):
        return iter([])


"apple" in q736a_0()
"pear" not in q736a_0()
