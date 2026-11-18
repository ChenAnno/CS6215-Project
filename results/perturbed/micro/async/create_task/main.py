import asyncio

def qa035_0():
    pass

async def qa035_2():
    qa035_0()

async def qa035_1():
    task = asyncio.create_task(qa035_2())
    await task

asyncio.run(qa035_1())
