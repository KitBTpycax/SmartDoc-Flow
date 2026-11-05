from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "👋 Вітаю у **SmartDoc Flow**!\n\n"
        "Надішліть мені документ (PDF, DOCX) або фотографію, щоб розпочати обробку.",
        parse_mode="Markdown"
    )