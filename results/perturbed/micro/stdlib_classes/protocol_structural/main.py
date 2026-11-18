from typing import Protocol


class qf4af_2(Protocol):
    def qf4af_3(self) -> str: ...


class qf4af_0:
    def qf4af_3(self) -> str:
        return "hello"


class qf4af_1:
    def qf4af_3(self) -> str:
        return "bonjour"


def qf4af_4(greeter: qf4af_2) -> str:
    return greeter.qf4af_3()


qf4af_4(qf4af_0())
