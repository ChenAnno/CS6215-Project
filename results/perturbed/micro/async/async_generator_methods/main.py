import asyncio

def q9973_1():
    pass

def q9973_0():
    pass

async def q9973_3():
    try:
        yield q9973_1
        yield q9973_1
    finally:
        q9973_0()

async def q9973_2():
    stream = q9973_3()
    async for handler in stream.__aiter__():
        handler()
        break
    await stream.__anext__()
    await stream.aclose()

asyncio.run(q9973_2())
