# 📄 SmartDoc Flow Bot

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Aiogram 3.x](https://img.shields.io/badge/Aiogram-3.x-blue)](https://docs.aiogram.dev/)
[![License: GNU AGPLv3](https://img.shields.io/badge/License-AGPL_3.0-orange.svg)](https://www.gnu.org/licenses/agpl-3.0.html)

**SmartDoc Flow** is an asynchronous multi-user document processing bot designed for automated document processing, optical character recognition (OCR), AI-driven content summarization using Google Gemini, and seamless document format conversion. Engineered with per-user data isolation, asynchronous SQLite caching, and proactive memory management, SmartDoc Flow ensures safe, fast, and multi-tenant document management.

---

## 🚀 Key Features

* 📖 **Optical Character Recognition (OCR):** Extracts text from images (`.jpg`, `.jpeg`, `.png`) and scanned PDF documents using Tesseract OCR with multi-language support (`ukr+eng`) at 300 DPI.
* 📑 **Hybrid Page-by-Page PDF Extraction:** Analyzes each PDF page individually; pages with embedded text are parsed directly, while scanned or image-only pages are processed via Tesseract OCR up to a maximum limit of 30 pages.
* 📝 **AI Summarization (TL;DR):** Leverages Google Gemini API to analyze document content and generate concise, structured summaries.
* 📄 **DOCX Export & Styling:** Converts raw extracted text or processed PDFs into beautifully formatted Microsoft Word (`.docx`) files with custom typography, margins, and styled headers.
* 🔎 **Indexed Page Search:** Performs case-insensitive keyword and phrase searches across specific page numbers in multi-page documents with safe HTML escaping.
* 🔒 **Strict User Data Isolation & Safety:** Implements user-scoped directory structures, UUID disk filenames, and SQLite records to prevent cross-user data exposure and Path Traversal.
* ⚡ **Performance Caching:** Extracts and caches document text upon initial upload to ensure instantaneous subsequent actions without re-running CPU-heavy OCR tasks.
* 🧹 **Automatic Disk Cleanup & 24h Text Retention:**
  * **Immediate File Deletion:** Uploaded source files and generated outputs (`.docx`, `.txt`) are deleted immediately from disk after processing and transmission.
  * **24-Hour Cache Retention:** Extracted document text is temporarily preserved in SQLite for 24 hours to enable fast follow-up actions, after which records are automatically pruned.
  * **Periodic Pruning:** An hourly background loop purges database records older than 24 hours and prunes temporary directory storage if total usage exceeds 500 MB.
* 📊 **Large Text Output Handling:** Automatically redirects text responses exceeding 3,900 characters into chat previews accompanied by clean downloadable `.txt` files.

---

## 🛠 Tech Stack

* **Language:** Python 3.9+
* **Bot Framework:** [Aiogram 3.x](https://github.com/aiogram/aiogram) (Async IO, FSM, Callbacks)
* **Database & ORM:** SQLAlchemy 2.0 (Async Engine) + SQLite (`aiosqlite`)
* **AI Engine:** Google Generative AI SDK (`google-genai` / Gemini 3.5 Flash Lite)
* **OCR & Rendering:** `pytesseract` + Tesseract OCR Engine, `pymupdf` (Fitz), `Pillow`
* **Document Processing:** `python-docx`
* **Concurrency:** `ThreadPoolExecutor` parallel worker pool for non-blocking asynchronous operations

---

## 📁 Project Structure

```text
smart_doc_bot/
├── bot/
│   ├── database/     # SQLAlchemy 2.0 models and async engine
│   ├── handlers/     # Bot routers (/start, upload, action callbacks)
│   ├── keyboards/    # Dynamic inline keyboard builder
│   ├── processors/   # OCR, PDF/DOCX handlers, and Gemini AI analyzer
│   ├── workers/      # Async thread-pool task executor
│   └── states.py     # FSM state definitions
├── temp_storage/     # User-isolated temporary file storage
├── config.py         # Centralized environment configurations
├── main.py           # Application entrypoint & periodic cleanup loop
├── requirements.txt  # Core project dependencies
└── README.md         # Documentation
```

---

## 📦 Installation & Setup

> [!IMPORTANT]
> **Оновлення бази даних:** Якщо ви оновлюєтеся зі старої версії бота, видаліть наявний файл `smart_doc.db` перед запуском, щоб нова схема SQLAlchemy 2.0 ініціалізувалася коректно.  
> *(If upgrading from an older version of the bot, delete any existing `smart_doc.db` file before running).*

### 1. Clone the Repository

```bash
git clone https://github.com/KitBTpycax/SmartDoc-Flow.git
cd SmartDoc-Flow
```

### 2. Create and Activate Virtual Environment

```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root directory (refer to `.env.example`):

```env
BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
DB_URL=sqlite+aiosqlite:///smart_doc.db
TEMP_DIR=temp_storage
TESSERACT_CMD=tesseract
```
*(On Windows, you may set `TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe` if Tesseract is not added to system PATH).*

### 5. Install Tesseract OCR

* **Linux:** `sudo apt install tesseract-ocr tesseract-ocr-ukr`
* **Windows:** Download and install [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki).
* Ensure Ukrainian (`ukr`) and English (`eng`) language packs are installed.

### 6. Run the Bot

```bash
python main.py
```

---

## 🛡️ Security & Privacy

* **Zero Secret Leakage:** Sensitive tokens and API credentials are kept strictly inside `.env` (ignored by Git).
* **Isolated File Access:** Database queries strictly check `user_id` ownership before processing any action callback or document request.
* **UUID Storage:** Files on disk are saved exclusively under unique UUIDs, eliminating Path Traversal risks.
* **Immediate Deletion & 24h Purging:** Raw uploaded files are discarded immediately after text extraction; cached text in SQLite is automatically purged after 24 hours.

---

## ⚖️ License

This project utilizes `pymupdf` (licensed under GNU AGPL v3). Consequently, this software is released under the **GNU Affero General Public License v3.0 (AGPL-3.0)**.

---

Developed with ❤️ by [KitBTpycax](https://github.com/KitBTpycax)
