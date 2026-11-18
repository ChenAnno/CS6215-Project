from dataclasses import dataclass, field


def q387c_1():
    return []


def q387c_2(name):
    return name.lower()


@dataclass
class q387c_0:
    name: str
    tags: list = field(default_factory=q387c_1)

    def __post_init__(self):
        self.name = q387c_2(self.name)


q387c_0("A")
