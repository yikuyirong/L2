import asyncio
import random

async def task_async(index)->(int,int):
    num = random.randint(1,5)
    await asyncio.sleep(num)
    print(f'{index} is complete')
    return (index,num)


async def main_async():
    result = await asyncio.gather(*[asyncio.create_task(task_async(i)) for i in range(1) ])
    
    print(result)




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main_async())
    loop.close()