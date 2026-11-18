import asyncio

def q1ff3_0():
    pass

async def q1ff3_2():
    q1ff3_0()

async def q1ff3_1():
    pending = q1ff3_2()
    pending.close()

asyncio.run(q1ff3_1())
