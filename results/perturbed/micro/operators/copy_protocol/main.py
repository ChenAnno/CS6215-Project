import copy


class qeb49_0:
    def __copy__(self):
        return qeb49_0()

    def __deepcopy__(self, memo):
        return qeb49_0()


config = qeb49_0()
copy.copy(config)
copy.deepcopy(config)
