from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_action_keyboard(file_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔍 Розпізнати текст (OCR)", callback_data=f"action_ocr:{file_id}")],
            [InlineKeyboardButton(text="📄 Сформувати DOCX", callback_data=f"action_docx:{file_id}")],
            [InlineKeyboardButton(text="📝 Стислий конспект (TL;DR)", callback_data=f"action_summarize:{file_id}")],
            [InlineKeyboardButton(text="🔎 Пошук у тексті", callback_data=f"action_search:{file_id}")]
        ]
    )