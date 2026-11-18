import asyncio

def q85c6_1():
    pass

async def q85c6_0():
    loop = asyncio.get_running_loop()
    loop.call_soon(q85c6_1)
    await asyncio.sleep(0)

asyncio.run(q85c6_0())
