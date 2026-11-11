import os
import uuid
from html import escape
from aiogram import Router, F, Bot
from aiogram.types import Message
from config import TEMP_DIR
from bot.database.engine import async_session
from bot.database.models import User, UploadedFile
from bot.keyboards.inline import get_action_keyboard
from bot.processors.pdf_service import extract_text_from_pdf
from bot.processors.ocr_service import perform_ocr
from bot.workers.task_queue import run_in_queue
from bot.processors.docx_service import extract_text_from_docx

router = Router()
ALLOWED_EXTENSIONS = ('.pdf', '.docx', '.jpg', '.jpeg', '.png')
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 МБ ліміт Telegram Bot API

@router.message(F.document | F.photo)
async def handle_file_upload(message: Message, bot: Bot):
    user_id = message.from_user.id
    username = message.from_user.username

    # 1. Перевірка розміру та отримання id файлу
    if message.document:
        if message.document.file_size > MAX_FILE_SIZE:
            await message.answer("❌ Файл занадто великий. Максимальний розмір — 20 МБ.")
            return
        file_id = message.document.file_id
        # Зберігаємо безпечне оригінальне ім'я виключно для відображення та збереження в БД
        raw_name = message.document.file_name or "document.pdf"
        file_name = os.path.basename(raw_name) or "document.pdf"
    else:
        file_id = message.photo[-1].file_id
        file_name = f"photo_{file_id[:8]}.jpg"

    file_ext = os.path.splitext(file_name)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        await message.answer("❌ Непідтримуваний формат файлу. Бот підтримує файли PDF, DOCX, JPG, PNG.")
        return

    msg = await message.answer("⏳ Завантажую та попередньо обробляю файл...")

    # 2. Створення персональної директорії та генерація виключно унікального UUID імені на диску
    user_dir = os.path.join(TEMP_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    unique_disk_name = f"{uuid.uuid4().hex}{file_ext}"
    local_path = os.path.join(user_dir, unique_disk_name)

    # 3. Скачування
    try:
        file_info = await bot.get_file(file_id)
        await bot.download_file(file_info.file_path, local_path)
    except Exception as e:
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except OSError:
                pass
        await msg.edit_text(f"❌ Помилка під час завантаження файлу: {escape(str(e))}", parse_mode="HTML")
        return

    # 4. Початкова екстракція тексту
    try:
        if file_ext == ".pdf":
            extracted_text = await run_in_queue(extract_text_from_pdf, local_path)
        elif file_ext == ".docx":
            extracted_text = await run_in_queue(extract_text_from_docx, local_path)    
        else:
            extracted_text = await run_in_queue(perform_ocr, local_path)

        if not extracted_text or not extracted_text.strip():
            raise RuntimeError("Не вдалося розпізнати або витягти текст із файлу.")
    except Exception as e:
        # Видаляємо файл з диска при збої екстракції та НЕ зберігаємо в БД
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except OSError:
                pass
        await msg.edit_text(f"❌ Помилка під час обробки файлу: {escape(str(e))}", parse_mode="HTML")
        return

    # 5. Запис у базу даних (обгорнуто в try...except для уникнення зависання статусу ⏳)
    try:
        async with async_session() as session:
            # Реєстрація або оновлення користувача
            db_user = await session.get(User, user_id)
            if not db_user:
                db_user = User(id=user_id, username=username)
                session.add(db_user)
            else:
                db_user.username = username
            
            # Додавання файлу (file_name — оригінальне ім'я для користувача)
            db_file = UploadedFile(
                user_id=user_id,
                file_name=file_name,
                file_path=local_path,
                file_type=file_ext.replace('.', ''),
                extracted_text=extracted_text
            )
            session.add(db_file)
            await session.commit()
            await session.refresh(db_file)

            safe_name = escape(file_name)
            await msg.edit_text(
                f"📥 Файл <b>{safe_name}</b> успішно завантажено та опрацьовано!\n"
                f"Оберіть потрібну дію нижче:",
                reply_markup=get_action_keyboard(db_file.id),
                parse_mode="HTML"
            )
    except Exception as e:
        await msg.edit_text(f"❌ Помилка збереження даних: {escape(str(e))}", parse_mode="HTML")
    finally:
        # Одразу видаляємо оригінальний завантажений файл з диска, адже текст збережено в БД
        if os.path.exists(local_path):
            try:
                os.remove(local_path)
            except OSError:
                pass
