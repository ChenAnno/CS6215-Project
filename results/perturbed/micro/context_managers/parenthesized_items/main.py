class q8770_0:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def q8770_2(self):
        pass


class q8770_1:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def q8770_3(self):
        pass


with (
    q8770_0() as reader,
    q8770_1() as writer,
):
    reader.q8770_2()
    writer.q8770_3()
