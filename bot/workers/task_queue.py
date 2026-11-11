import asyncio
from concurrent.futures import ThreadPoolExecutor

# Пул потоків на 4 воркери для паралельної обробки важких CPU-задач (OCR, PDF, DOCX)
executor = ThreadPoolExecutor(max_workers=4)
task_queue = asyncio.Queue()

async def worker():
    """Фоновий воркер для паралельної обробки черги задач"""
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
    """
    Виконує блокуючу задачу в пулі потоків напряму без затримок у черзі
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(executor, func, *args)
