import os
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, FSInputFile
from aiogram.fsm.context import FSMContext
from config import TEMP_DIR
from bot.processors.pdf_service import extract_text_from_pdf
from bot.processors.ocr_service import perform_ocr
from bot.processors.docx_service import create_formatted_docx
from bot.processors.analyzer import summarize_text_sync, search_in_text
from bot.workers.task_queue import run_in_queue
from bot.states import SearchState

router = Router()
ALLOWED_EXTENSIONS = ('.pdf', '.jpg', '.jpeg', '.png')

def get_latest_source_file():
    files = [
        os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR)
        if os.path.isfile(os.path.join(TEMP_DIR, f)) and f.lower().endswith(ALLOWED_EXTENSIONS)
    ]
    if not files:
        return None
    return max(files, key=os.path.getmtime)

@router.callback_query(F.data.startswith("action_"))
async def handle_actions(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await callback.answer()
    action = callback.data
    
    latest_file = get_latest_source_file()
    if not latest_file:
        await callback.message.answer("❌ Файл не знайдено. Будь ласка, завантажте файл знову.")
        return

    file_ext = os.path.splitext(latest_file)[1].lower()

    if action == "action_search":
        await state.set_state(SearchState.waiting_for_query)
        await callback.message.answer("🔎 Введіть слово або фразу для пошуку у цьому файлі:")
        return

    msg = await callback.message.answer("⏳ Обробляю ваш запит...")

    try:
        if action == "action_ocr":
            if file_ext == ".pdf":
                text = await run_in_queue(extract_text_from_pdf, latest_file)
            else:
                text = await run_in_queue(perform_ocr, latest_file)
            
            res_text = f"📖 **Розпізнаний текст:**\n\n{text}"
            if len(res_text) > 3900:
                res_text = res_text[:3800] + "..."
            try:
                await msg.edit_text(res_text, parse_mode="Markdown")
            except Exception:
                await msg.edit_text(res_text)

        elif action == "action_docx":
            if file_ext == ".pdf":
                text = await run_in_queue(extract_text_from_pdf, latest_file)
            else:
                text = await run_in_queue(perform_ocr, latest_file)
            
            out_docx = os.path.join(TEMP_DIR, "formatted_document.docx")
            await run_in_queue(create_formatted_docx, text, out_docx)
            await callback.message.answer_document(
                FSInputFile(out_docx, filename="formatted_document.docx"),
                caption="📄 Документ успішно відформатовано в DOCX!"
            )
            await msg.delete()

        elif action == "action_summarize":
            if file_ext == ".pdf":
                text = await run_in_queue(extract_text_from_pdf, latest_file)
            else:
                text = await run_in_queue(perform_ocr, latest_file)
            
            summary = await run_in_queue(summarize_text_sync, text)
            res_summary = f"📝 **Стислий конспект (Gemini AI):**\n\n{summary}"
            if len(res_summary) > 3900:
                res_summary = res_summary[:3800] + "..."
            
            try:
                await msg.edit_text(res_summary, parse_mode="Markdown")
            except Exception:
                await msg.edit_text(res_summary)

    except Exception as e:
        await msg.edit_text(f"❌ Помилка при обробці: {e}")

@router.message(SearchState.waiting_for_query)
async def process_search_query(message: Message, state: FSMContext):
    query = message.text.strip()
    latest_file = get_latest_source_file()
    
    if not latest_file:
        await message.answer("❌ Вихідний файл не знайдено. Надішліть документ знову.")
        await state.clear()
        return

    file_ext = os.path.splitext(latest_file)[1].lower()
    msg = await message.answer(f"🔎 Шукаю `{query}` у документі...", parse_mode="Markdown")

    if file_ext == ".pdf":
        text = await run_in_queue(extract_text_from_pdf, latest_file)
    else:
        text = await run_in_queue(perform_ocr, latest_file)

    results = search_in_text(text, query)
    await state.clear()

    if not results:
        await msg.edit_text(f"❌ Запиту `{query}` не знайдено в документі.", parse_mode="Markdown")
    else:
        output = f"🎯 **Результати пошуку для:** `{query}`\n\n" + "\n\n".join(results[:5])
        if len(output) > 3900:
            output = output[:3800] + "..."
        try:
            await msg.edit_text(output, parse_mode="Markdown")
        except Exception:
            await msg.edit_text(output)