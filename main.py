import sys
import io
import asyncio
import logging

# Примусово вмикаємо UTF-8 кодування для потоків виводу Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot.database.engine import init_db
from bot.workers.task_queue import worker
from bot.handlers import start, upload, actions

logging.basicConfig(level=logging.INFO)

# Приглушуємо детальні логи сторонніх бібліотек, які спричиняють помилки кодування в терміналі
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

async def main():
    await init_db()
    
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(upload.router)
    dp.include_router(actions.router)

    # Фоновий воркер черги завдань
    asyncio.create_task(worker())

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())