import asyncio

async def qf242_0():
    return 1

async def qf242_1():
    return await qf242_0()

asyncio.run(qf242_1())
