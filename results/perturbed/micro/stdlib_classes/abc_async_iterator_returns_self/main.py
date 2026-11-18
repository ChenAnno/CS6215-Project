import asyncio
from collections.abc import AsyncIterator

def qcd48_1():
    pass

class qcd48_0(AsyncIterator):
    def __init__(self):
        self.done = False

    async def __anext__(self):
        if self.done:
            raise StopAsyncIteration
        self.done = True
        return qcd48_1

async def qcd48_2():
    async for handler in qcd48_0():
        handler()

asyncio.run(qcd48_2())
