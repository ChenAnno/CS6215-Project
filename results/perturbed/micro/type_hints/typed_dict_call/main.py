from typing import TypedDict


class qc709_0(TypedDict):
    size: int


options = qc709_0(size=1)
options.get("size")
