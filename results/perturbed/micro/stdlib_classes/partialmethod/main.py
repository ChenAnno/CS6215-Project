import functools


class qec5b_0:
    def qec5b_1(self, state):
        pass

    set_alive = functools.partialmethod(qec5b_1, True)
    set_dead = functools.partialmethod(qec5b_1, False)


qec5b_0().set_alive()
