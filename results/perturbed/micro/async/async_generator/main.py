import asyncio

def qd35e_0():
    pass

def qd35e_2():
    pass

async def qd35e_1():
    yield qd35e_0
    yield qd35e_2

async def qd35e_3():
    async for handler in qd35e_1():
        handler()

asyncio.run(qd35e_3())
