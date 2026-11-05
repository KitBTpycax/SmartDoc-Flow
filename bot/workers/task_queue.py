import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=4)
task_queue = asyncio.Queue()

async def worker():
    while True:
        func, args, future = await task_queue.get()
        loop = asyncio.get_running_loop()
        try:
            result = await loop.run_in_executor(executor, func, *args)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
        finally:
            task_queue.task_done()

async def run_in_queue(func, *args):
    loop = asyncio.get_running_loop()
    future = loop.create_future()
    await task_queue.put((func, args, future))
    return await future