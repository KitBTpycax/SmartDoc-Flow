import os
from html import escape
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext

from config import TEMP_DIR
from bot.database.engine import async_session
from bot.database.models import UploadedFile
from bot.processors.docx_service import create_formatted_docx
from bot.processors.analyzer import summarize_text_sync, search_in_text
from bot.workers.task_queue import run_in_queue
from bot.states import SearchState

router = Router()

async def send_formatted_result(
    callback: CallbackQuery,
    msg: Message,
    title: str,
    full_text: str,
    caption: str,
    user_id: int
):
    """
    Надсилає результат у чат. Якщо довжина перевищує 3900 символів —
    надсилає коротке прев'ю в чат та прикріплює повний текст файлом result.txt,
    після чого видаляє файл з диска у блоці finally.
    """
    formatted_msg = f"{title}\n\n{escape(full_text)}"
    if len(formatted_msg) <= 3900:
        await msg.edit_text(formatted_msg, parse_mode="HTML")
        return

    # Довжина перевищує 3900 символів: надсилаємо прев'ю та файл result.txt
    preview_slice = full_text[:1000]
    preview_text = (
        f"{title}\n\n"
        f"{escape(preview_slice)}...\n\n"
        f"<i>📎 Повний текст перевищує 3900 символів та прикріплений нижче у файлі result.txt</i>"
    )
    await msg.edit_text(preview_text, parse_mode="HTML")

    user_dir = os.path.join(TEMP_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    temp_txt_path = os.path.join(user_dir, f"result_{callback.id}.txt")
    try:
        with open(temp_txt_path, "w", encoding="utf-8") as f:
            f.write(full_text)
        await callback.message.answer_document(
            FSInputFile(temp_txt_path, filename="result.txt"),
            caption=caption
        )
    finally:
        if os.path.exists(temp_txt_path):
            try:
                os.remove(temp_txt_path)
            except OSError:
                pass

@router.callback_query(F.data.startswith("action_"))
async def handle_actions(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    
    # Парсимо дію та file_id (наприклад action_ocr:15)
    parts = callback.data.split(":")
    if len(parts) != 2:
        return
    
    action, file_id_str = parts[0], parts[1]
    file_id = int(file_id_str)
    user_id = callback.from_user.id

    # Зчитуємо файл із БД з перевіркою власника
    async with async_session() as session:
        db_file = await session.get(UploadedFile, file_id)
        if not db_file or db_file.user_id != user_id:
            await callback.message.answer("❌ Файл не знайдено або доступ заборонено.")
            return
        
        extracted_text = db_file.extracted_text or ""

    if action == "action_search":
        await state.set_state(SearchState.waiting_for_query)
        await state.update_data(search_file_id=file_id)
        await callback.message.answer("🔎 Введіть слово або фразу для пошуку у цьому файлі:")
        return

    msg = await callback.message.answer("⏳ Обробляю ваш запит...")

    try:
        if action == "action_ocr":
            text_to_show = extracted_text if extracted_text.strip() else "Текст не знайдено або порожній."
            await send_formatted_result(
                callback=callback,
                msg=msg,
                title="📖 <b>Розпізнаний текст:</b>",
                full_text=text_to_show,
                caption="📖 Повний розпізнаний текст",
                user_id=user_id
            )

        elif action == "action_docx":
            user_dir = os.path.join(TEMP_DIR, str(user_id))
            os.makedirs(user_dir, exist_ok=True)
            out_docx = os.path.join(user_dir, f"formatted_{file_id}.docx")
            try:
                await run_in_queue(create_formatted_docx, extracted_text, out_docx)
                base_name = os.path.splitext(db_file.file_name)[0]
                await callback.message.answer_document(
                    FSInputFile(out_docx, filename=f"formatted_{base_name}.docx"),
                    caption="📄 Документ успішно відформатовано в DOCX!"
                )
                await msg.delete()
            finally:
                if os.path.exists(out_docx):
                    try:
                        os.remove(out_docx)
                    except OSError:
                        pass

        elif action == "action_summarize":
            summary = await run_in_queue(summarize_text_sync, extracted_text)
            await send_formatted_result(
                callback=callback,
                msg=msg,
                title="📝 <b>Стислий конспект (Gemini AI):</b>",
                full_text=summary,
                caption="📝 Повний стислий конспект",
                user_id=user_id
            )

    except Exception as e:
        await msg.edit_text(f"❌ Помилка при обробці: {escape(str(e))}", parse_mode="HTML")

@router.message(SearchState.waiting_for_query, F.text)
async def process_search_query(message: Message, state: FSMContext):
    try:
        query = message.text.strip()
        data = await state.get_data()
        file_id = data.get("search_file_id")
        user_id = message.from_user.id

        async with async_session() as session:
            db_file = await session.get(UploadedFile, file_id)
            if not db_file or db_file.user_id != user_id:
                await message.answer("❌ Файл не знайдено.")
                return
            extracted_text = db_file.extracted_text or ""

        msg = await message.answer(f"🔎 Шукаю <code>{escape(query)}</code>...", parse_mode="HTML")
        results = search_in_text(extracted_text, query)

        if not results:
            await msg.edit_text(f"❌ Запиту <code>{escape(query)}</code> не знайдено.", parse_mode="HTML")
        else:
            output = f"🎯 <b>Результати пошуку для:</b> <code>{escape(query)}</code>\n\n" + "\n\n".join(results[:5])
            if len(output) > 3900:
                output = output[:3800] + "..."
            await msg.edit_text(output, parse_mode="HTML")
    finally:
        await state.clear()
