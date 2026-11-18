import asyncio

async def q2a0c_0():
    pass

async def q2a0c_2(coro):
    await coro

async def q2a0c_1():
    pending = q2a0c_0()
    await q2a0c_2(pending)

asyncio.run(q2a0c_1())
