import asyncio

class qd36b_0:
    def __init__(self, n):
        self.n = n

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self.n == 0:
            raise StopAsyncIteration
        self.n -= 1
        return self.n

async def qd36b_1():
    async for _ in qd36b_0(2):
        pass

asyncio.run(qd36b_1())
