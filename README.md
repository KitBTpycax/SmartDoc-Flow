# 📄 SmartDoc Flow Bot

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Aiogram 3.x](https://img.shields.io/badge/Aiogram-3.x-blue)](https://docs.aiogram.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**SmartDoc Flow** is a high-performance, asynchronous Telegram bot designed for automated document processing, optical character recognition (OCR), AI-driven content summarization using Google Gemini, and seamless document format conversion. Engineered with per-user data isolation, asynchronous SQLite caching, and proactive memory management, SmartDoc Flow ensures safe, fast, and multi-tenant document management.

---

## 🚀 Key Features

* 📖 **Optical Character Recognition (OCR):** Extracts text from images (`.jpg`, `.jpeg`, `.png`) and scanned PDF documents using Tesseract OCR with multi-language support (`ukr+eng`).
* 📝 **AI Summarization (TL;DR):** Leverages Google Gemini API to analyze document content and generate concise, structured summaries.
* 📄 **DOCX Export & Styling:** Converts raw extracted text or processed PDFs into beautifully formatted Microsoft Word (`.docx`) files with custom typography, margins, and styled headers.
* 🔎 **Indexed Page Search:** Performs case-insensitive keyword and phrase searches across specific page numbers in multi-page documents.
* 🔒 **Strict User Data Isolation:** Implements user-scoped directory structures and SQLite records to prevent cross-user data exposure.
* ⚡ **Performance Caching:** Extracts and caches document text upon initial upload to ensure instantaneous subsequent actions without re-running CPU-heavy OCR tasks.
* 🧹 **Automatic Disk Cleanup & Memory Safety:**
  * **Immediate Deletion:** Uploaded source files and generated outputs (`.docx`, `.txt`) are deleted immediately after processing and transmission.
  * **Proactive Storage Pruning:** Startup routine monitors temporary storage and automatically purges the oldest cached items if total directory usage exceeds 500 MB.
* 📊 **Large Text Output Handling:** Automatically redirects text responses exceeding 3,900 characters into chat previews accompanied by clean downloadable `.txt` files.

---

## 🛠 Tech Stack

* **Language:** Python 3.9+
* **Bot Framework:** [Aiogram 3.x](https://github.com/aiogram/aiogram) (Async IO, FSM, Callbacks)
* **Database & ORM:** SQLAlchemy (Async Engine) + SQLite (`aiosqlite`)
* **AI Engine:** Google Generative AI SDK (`google-genai` / Gemini 3.5 Flash Lite)
* **OCR & Rendering:** `pytesseract` + Tesseract OCR Engine, `pymupdf` (Fitz), `Pillow`
* **Document Processing:** `python-docx`, `pypdf`
* **Concurrency:** `ThreadPoolExecutor` offloading for non-blocking asynchronous operations

---

## 📁 Project Structure

```text
smart_doc_bot/
├── bot/
│   ├── database/     # SQLAlchemy models and async engine
│   ├── handlers/     # Bot routers (/start, upload, action callbacks)
│   ├── keyboards/    # Dynamic inline keyboard builder
│   ├── processors/   # OCR, PDF/DOCX handlers, and Gemini AI analyzer
│   ├── workers/      # Async thread-pool task queue executor
│   └── states.py     # FSM state definitions
├── temp_storage/     # User-isolated temporary file storage
├── config.py         # Centralized environment configurations
├── main.py           # Application entrypoint & storage cleanup runner
├── requirements.txt  # Project dependencies
└── README.md         # Documentation
```

---

## 📦 Installation & Setup

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
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 5. Install Tesseract OCR

* Download and install [Tesseract OCR for Windows](https://github.com/UB-Mannheim/tesseract/wiki) or install via package manager on Linux (`sudo apt install tesseract-ocr tesseract-ocr-ukr`).
* Ensure Ukrainian and English language packs are installed.
* Update `TESSERACT_CMD` in your `.env` file to match your system binary path if necessary.

### 6. Run the Bot

```bash
python main.py
```

---

## 🛡️ Security & Privacy

* **Zero Secret Leakage:** Sensitive tokens and API credentials are kept strictly inside `.env` (ignored by Git).
* **Isolated File Access:** Database queries strictly check `user_id` ownership before processing any action callback or document request.
* **Ephemeral Storage:** Raw uploaded documents are discarded immediately after text extraction to protect user confidentiality.

---

Developed with ❤️ by [KitBTpycax](https://github.com/KitBTpycax)
