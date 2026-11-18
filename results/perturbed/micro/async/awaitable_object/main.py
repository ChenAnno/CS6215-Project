import asyncio

async def q0e4a_1():
    pass

class q0e4a_0:
    def __await__(self):
        return q0e4a_1().__await__()

async def q0e4a_2():
    await q0e4a_0()

asyncio.run(q0e4a_2())
