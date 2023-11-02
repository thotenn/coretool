import asyncio
import time


async def say_after(delay, what):
    await asyncio.sleep(delay)
    print(what)

async def main(): # tareas ejecutadas de forma secuencial
    print(f"started at {time.strftime('%X')}")
    await say_after(3, 'hello')
    await say_after(0, 'world')
    print(f"finished at {time.strftime('%X')}")

async def main_para(): # tareas ejecutadas de forma paralela
    print(f"started at {time.strftime('%X')}")
    t1 = say_after(4, 'hello')
    t2 = say_after(1, 'world')
    await asyncio.gather(t1, t2)
    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())