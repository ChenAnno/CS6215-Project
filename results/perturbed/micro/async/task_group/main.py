import asyncio

async def qdc89_1():
    pass

async def qdc89_0():
    async with asyncio.TaskGroup() as group:
        group.create_task(qdc89_1())

asyncio.run(qdc89_0())
