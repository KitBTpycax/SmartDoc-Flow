import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///smart_doc.db")
TEMP_DIR = os.getenv("TEMP_DIR", "temp_storage")
TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

os.makedirs(TEMP_DIR, exist_ok=True)