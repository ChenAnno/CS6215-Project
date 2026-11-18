import asyncio

def q6fe8_0():
    pass

async def q6fe8_2(value):
    return value

async def q6fe8_1():
    handlers = (await q6fe8_2(handler) for handler in [q6fe8_0])
    async for handler in handlers.__aiter__():
        handler()
    await handlers.aclose()

asyncio.run(q6fe8_1())
