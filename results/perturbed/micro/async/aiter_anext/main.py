import asyncio

async def qbd65_1():
    yield 1

async def qbd65_0():
    iterator = aiter(qbd65_1())
    await anext(iterator)

asyncio.run(qbd65_0())
