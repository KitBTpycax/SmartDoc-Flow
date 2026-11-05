from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_file_action_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Розпізнати текст (OCR)", callback_data="action_ocr")],
            [InlineKeyboardButton(text="📄 Сформувати DOCX", callback_data="action_docx")],
            [InlineKeyboardButton(text="📝 Стислий конспект (TL;DR)", callback_data="action_summarize")],
            [InlineKeyboardButton(text="🔎 Пошук у тексті", callback_data="action_search")]
        ]
    )