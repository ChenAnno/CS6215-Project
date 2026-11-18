import asyncio

async def qe35a_1():
    yield 1
    yield 2

async def qe35a_0(n):
    return n * 2

async def qe35a_2():
    return [await qe35a_0(n) async for n in qe35a_1()]

asyncio.run(qe35a_2())
