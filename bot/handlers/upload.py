import os
import uuid
from aiogram import Router, F, Bot
from aiogram.types import Message
from config import TEMP_DIR
from bot.keyboards.inline import get_file_action_kb

router = Router()

@router.message(F.document | F.photo)
async def handle_file_upload(message: Message, bot: Bot):
    if message.document:
        file_id = message.document.file_id
        display_name = message.document.file_name or "document.pdf"
        ext = os.path.splitext(display_name)[1] or ".pdf"
    else:
        file_id = message.photo[-1].file_id
        display_name = f"photo_{message.photo[-1].file_unique_id}.jpg"
        ext = ".jpg"

    # Генерація безпечного імені файлу для ОС Windows та httpx
    safe_filename = f"file_{uuid.uuid4().hex[:8]}{ext}"
    local_path = os.path.join(TEMP_DIR, safe_filename)

    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, local_path)

    await message.answer(
        f"📥 Файл `{display_name}` успішно завантажено!\nОберіть потрібну дію нижче:",
        reply_markup=get_file_action_kb(),
        parse_mode="Markdown"
    )