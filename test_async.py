import asyncio

async def f1():
    print("f1 start")
    await asyncio.sleep(1)
    print("f1 end")
    
async def f2():
    print("f2 start")
    await asyncio.sleep(2)
    print("f2 end")
    
loop = asyncio.get_event_loop()
t1 = loop.create_task(f1())
t2 = loop.create_task(f2())
loop.run_until_complete(asyncio.gather(t1, t2))
