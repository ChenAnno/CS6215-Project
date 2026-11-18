class q7007_0:
    @property
    def name(self):
        return "ada"

message = "{.name}".format(q7007_0())
