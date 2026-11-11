import sys
import io
import os
import asyncio
import logging

# Примусово вмикаємо UTF-8 кодування для потоків виводу Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from aiogram import Bot, Dispatcher
from config import BOT_TOKEN, TEMP_DIR
from bot.database.engine import init_db, async_session
from bot.database.models import cleanup_old_records
from bot.workers.task_queue import worker
from bot.handlers import start, upload, actions

logging.basicConfig(level=logging.INFO)

# Приглушуємо детальні логи сторонніх бібліотек, які спричиняють помилки кодування в терміналі
logging.getLogger("google_genai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

def cleanup_temp_storage(temp_dir: str = TEMP_DIR, max_size_bytes: int = 500 * 1024 * 1024):
    """
    Перевіряє загальний об'єм папки temp_storage.
    Якщо загальний об'єм перевищує 500 МБ, видаляє найстаріші файли (зберігаючи .gitkeep).
    """
    if not os.path.exists(temp_dir):
        return

    files = []
    total_size = 0
    for root, _, filenames in os.walk(temp_dir):
        for fname in filenames:
            if fname == ".gitkeep":
                continue
            file_path = os.path.join(root, fname)
            try:
                stat = os.stat(file_path)
                files.append((file_path, stat.st_mtime, stat.st_size))
                total_size += stat.st_size
            except OSError:
                pass

    if total_size <= max_size_bytes:
        return

    logging.info(
        f"Загальний об'єм {temp_dir} ({total_size / (1024 * 1024):.2f} MB) перевищує ліміт "
        f"({max_size_bytes / (1024 * 1024):.0f} MB). Видалення найстаріших файлів..."
    )

    # Сортуємо файли від найстаріших до найновіших
    files.sort(key=lambda x: x[1])

    for file_path, _, size in files:
        try:
            os.remove(file_path)
            total_size -= size
            logging.info(f"Видалено файл для звільнення місця: {file_path}")
        except OSError as e:
            logging.warning(f"Не вдалося видалити {file_path}: {e}")

        if total_size <= max_size_bytes:
            break

    # Видалення порожніх піддиректорій (крім кореня temp_dir)
    for root, _, _ in os.walk(temp_dir, topdown=False):
        if os.path.abspath(root) != os.path.abspath(temp_dir):
            try:
                if not os.listdir(root):
                    os.rmdir(root)
            except OSError:
                pass

async def periodic_cleanup():
    """
    Фоновий цикл очищення: щогодини викликає cleanup_old_records (видалення записів,
    старіших за 24 години) та cleanup_temp_storage (контроль об'єму до 500 МБ).
    """
    while True:
        try:
            cleanup_temp_storage()
            async with async_session() as session:
                deleted_count = await cleanup_old_records(session, hours=24)
                if deleted_count > 0:
                    logging.info(f"Періодичне очищення: видалено {deleted_count} застарілих записів з БД.")
        except Exception as e:
            logging.warning(f"Помилка під час періодичного очищення: {e}")

        await asyncio.sleep(3600)

async def main():
    await init_db()

    # Запуск фонової задачі періодичного очищення сховища та БД
    asyncio.create_task(periodic_cleanup())

    # Запуск 4 паралельних воркерів черги задач
    for _ in range(4):
        asyncio.create_task(worker())

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(start.router)
    dp.include_router(upload.router)
    dp.include_router(actions.router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
