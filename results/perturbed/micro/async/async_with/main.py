import asyncio

class q876b_0:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def q876b_1(self):
        pass

async def q876b_2():
    async with q876b_0() as session:
        await session.q876b_1()

asyncio.run(q876b_2())
